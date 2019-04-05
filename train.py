from __future__ import print_function
import argparse
import os
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
import numpy as np

from model import capsules
from loss import SpreadLoss

# Training settings
parser = argparse.ArgumentParser(description='PyTorch Matrix-Capsules-EM')
parser.add_argument('--batch-size', type=int, default=2, metavar='N',
					help='input batch size for training (default: 20)')
parser.add_argument('--test-batch-size', type=int, default=2, metavar='N',
					help='input batch size for testing (default: 20)')
parser.add_argument('--test-intvl', type=int, default=1, metavar='N',
					help='test intvl (default: 1)')
parser.add_argument('--epochs', type=int, default=25, metavar='N',
					help='number of epochs to train (default: 25)')
parser.add_argument('--lr', type=float, default=0.01, metavar='LR',
					help='learning rate (default: 0.01)')
parser.add_argument('--weight-decay', type=float, default=0, metavar='WD',
					help='weight decay (default: 0)')
parser.add_argument('--no-cuda', action='store_true', default=False,
					help='disables CUDA training')
parser.add_argument('--seed', type=int, default=1, metavar='S',
					help='random seed (default: 1)')
parser.add_argument('--log-interval', type=int, default=10, metavar='N',
					help='how many batches to wait before logging training status')
parser.add_argument('--em-iters', type=int, default=2, metavar='N',
					help='iterations of EM Routing')
parser.add_argument('--snapshot-folder', type=str, default='./snapshots', metavar='SF',
					help='where to store the snapshots')
parser.add_argument('--data-folder', type=str, default='./processed', metavar='DF',
					help='where to store the datasets')
parser.add_argument('--network-length', type=int, default=5, metavar='N',
					help='length of network (defalut: 5)')

def npy_loader(path):

	sample = torch.from_numpy(np.load(path))
	img_transform=transforms.Compose([
						  transforms.Resize((50,50)),
						  transforms.RandomHorizontalFlip(),
						  transforms.ToTensor(),
						  transforms.Normalize((0.2307,), (0.3081,))
					  ])
	for i in range(0,sample.size()[0]):
		img = transforms.ToPILImage(mode='L')(sample[i,:,:])
		img_tensor = img_transform(img)
		if i == 0:
			img = transforms.ToPILImage(mode='L')(sample[i,:,:])
			img_tensor = img_transform(img)
		else:
			img = transforms.ToPILImage(mode='L')(sample[i,:,:])
			temp_tensor = img_transform(img)
			img_tensor = torch.stack((img_tensor,temp_tensor),0)
	print(img_tensor.size())
	print("||Size of img_tensor ")
	return img_tensor



def get_setting(args):
	kwargs = {'num_workers': 1, 'pin_memory': True} if args.cuda else {}
	path = os.path.join(args.data_folder)

	if os.path.exists(os.path.dirname(path)):
		num_class = 6
		train_loader = torch.utils.data.DataLoader(
			datasets.DatasetFolder(
			 root=path,
			 loader=npy_loader,
			 extensions=['.npy']
			),
			batch_size=args.batch_size, shuffle=True, **kwargs)
		test_loader = torch.utils.data.DataLoader(
			datasets.DatasetFolder(
			 root=path,
			 loader=npy_loader,
			 extensions=['.npy']
			),
			batch_size=args.test_batch_size, shuffle=True, **kwargs)
	else:
		raise NameError('Undefined dataset {}'.format(args.dataset))
	return num_class, train_loader, test_loader


def accuracy(output, target, topk=(1,)):
	"""Computes the precision@k for the specified values of k"""
	maxk = max(topk)
	batch_size = target.size(0)

	_, pred = output.topk(maxk, 1, True, True)
	pred = pred.t()
	correct = pred.eq(target.view(1, -1).expand_as(pred))

	res = []
	for k in topk:
		correct_k = correct[:k].view(-1).float().sum(0, keepdim=True)
		res.append(correct_k.mul_(100.0 / batch_size))
	return res


class AverageMeter(object):
	"""Computes and stores the average and current value"""
	def __init__(self):
		self.reset()

	def reset(self):
		self.val = 0
		self.avg = 0
		self.sum = 0
		self.count = 0

	def update(self, val, n=1):
		self.val = val
		self.sum += val * n
		self.count += n
		self.avg = self.sum / self.count


def train(train_loader, model, criterion, optimizer, epoch, device):

	batch_time = AverageMeter()
	data_time = AverageMeter()

	model.train()
	train_len = len(train_loader)
	epoch_acc = 0
	end = time.time()

	for batch_idx, (data, target) in enumerate(train_loader):
		#print(batch_idx)
		#print("bbbbbbbbbbb")
		#print((data,target))
		#print(data.shape())
		#print(type(data))
		data_time.update(time.time() - end)

		data, target = data.to(device), target.to(device)
		optimizer.zero_grad()
		output = model(data)
		r = (1.*batch_idx + (epoch-1)*train_len) / (args.epochs*train_len)
		loss = criterion(output, target, r)
		acc = accuracy(output, target)
		loss.backward()
		optimizer.step()

		batch_time.update(time.time() - end)
		end = time.time()

		epoch_acc += acc[0].item()
		if batch_idx % args.log_interval == 0:
			print('Train '+str(part_no)+' Epoch: {}\t[{}/{} ({:.0f}%)]\t'
				  'Loss: {:.6f}\tAccuracy: {:.6f}\t'
				  'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
				  'Data {data_time.val:.3f} ({data_time.avg:.3f})'.format(
				  epoch, batch_idx * len(data), len(train_loader.dataset),
				  100. * batch_idx / len(train_loader),
				  loss.item(), acc[0].item(),
				  batch_time=batch_time, data_time=data_time))
	return epoch_acc


def snapshot(model, folder, epoch,part_no):
	path = os.path.join(folder, str(part_no), 'model_{}.pth'.format(epoch))
	if not os.path.exists(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))
	print('saving model to {}'.format(path))
	torch.save(model.state_dict(), path)


def test(test_loader, model, criterion, device):

	model.eval()
	test_loss = 0
	acc = 0
	test_len = len(test_loader)
	with torch.no_grad():
		for data, target in test_loader:
			print("bbbbbbbbbbb")
			#print((data,target))
			print(type(data))
			print(data.size())

			data, target = data.to(device), target.to(device)
			output = model(data)
			test_loss += criterion(output, target, r=1).item()
			acc += accuracy(output, target)[0].item()

	test_loss /= test_len
	acc /= test_len
	print('\nTest set '+str(part_no)+': Average loss: {:.6f}, Accuracy: {:.6f} \n'.format(
		test_loss, acc))
	with open("log.txt", "a") as f:
	 f.write('\nTest set '+str(part_no)+': Average loss: {:.6f}, Accuracy: {:.6f} \n'.format(
		test_loss, acc))
	return acc


def main():
	global args, best_prec1, part_no
	args = parser.parse_args()
	args.cuda = not args.no_cuda and torch.cuda.is_available()
	open('log.txt', 'w').close()

	torch.manual_seed(args.seed)
	if args.cuda:
		torch.cuda.manual_seed(args.seed)

	device = torch.device("cuda" if args.cuda else "cpu")
	

# datasets
	num_class, train_loader, test_loader = get_setting(args)

	# model
	#A, B, C, D = 64, 8, 16, 16
	A, B, C, D = 32, 32, 32, 32
	model = capsules(A=A, B=B, C=C, D=D, E=num_class,
						iters=args.em_iters).to(device)

	criterion = SpreadLoss(num_class=num_class, m_min=0.2, m_max=0.9)
	optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
	scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=1)

	best_acc = test(test_loader, model, criterion, device)
	for epoch in range(1, args.epochs + 1):
		acc = train(train_loader, model, criterion, optimizer, epoch, device)
		acc /= len(train_loader)
		scheduler.step(acc)
		if epoch % args.test_intvl == 0:
			best_acc = max(best_acc, test(test_loader, model, criterion, device))
	best_acc = max(best_acc, test(test_loader, model, criterion, device))
	print('best test accuracy for net no '+str(i)+': {:.6f}'.format(best_acc))

	snapshot(model, args.snapshot_folder, args.epochs,part_no)
	

if __name__ == '__main__':
	main()
