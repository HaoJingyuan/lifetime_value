import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np

# 生成数据集
class LinearDataset(Dataset):
    def __init__(self, num_samples, input_dim, noise_std=0.1):
        """
        初始化数据集
        :param num_samples: 样本数量
        :param input_dim: 输入维度
        :param noise_std: 噪声标准差
        """
        # 随机生成权重
        self.true_weights = torch.randn(input_dim, 1)
        # 随机生成输入数据
        self.inputs = torch.randn(num_samples, input_dim)
        # 根据线性关系生成目标值，并添加噪声
        self.targets = torch.matmul(self.inputs, self.true_weights) + torch.randn(num_samples, 1) * noise_std

    def __len__(self):
        """
        返回数据集的长度
        :return: 数据集长度
        """
        return len(self.inputs)

    def __getitem__(self, idx):
        """
        根据索引返回对应的样本和标签
        :param idx: 样本索引
        :return: 样本和标签
        """
        return self.inputs[idx], self.targets[idx]

# 定义线性模型
class LinearModel(nn.Module):
    def __init__(self, input_dim):
        """
        初始化线性模型
        :param input_dim: 输入维度
        """
        super(LinearModel, self).__init__()
        self.linear = nn.Linear(input_dim, 1)

    def forward(self, x):
        """
        前向传播
        :param x: 输入数据
        :return: 模型输出
        """
        return self.linear(x)

# 训练模型
def train_model(model, train_loader, criterion, optimizer, epochs):
    """
    训练线性模型
    :param model: 线性模型
    :param train_loader: 训练数据加载器
    :param criterion: 损失函数
    :param optimizer: 优化器
    :param epochs: 训练轮数
    """
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f'Epoch {epoch + 1}/{epochs}, Loss: {running_loss / len(train_loader)}')

# 测试模型
def test_model(model, test_loader, criterion):
    """
    测试线性模型
    :param model: 线性模型
    :param test_loader: 测试数据加载器
    :param criterion: 损失函数
    :return: 测试损失
    """
    model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for inputs, targets in test_loader:
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            test_loss += loss.item()
    return test_loss / len(test_loader)

# 主函数
if __name__ == "__main__":
    # 数据集参数
    num_samples = 1000
    input_dim = 10
    batch_size = 32
    epochs = 10

    # 生成数据集
    train_dataset = LinearDataset(num_samples, input_dim)
    test_dataset = LinearDataset(int(num_samples * 0.2), input_dim)

    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # 初始化模型、损失函数和优化器
    model = LinearModel(input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    # 训练模型
    train_model(model, train_loader, criterion, optimizer, epochs)

    # 测试模型
    test_loss = test_model(model, test_loader, criterion)
    print(f'Test Loss: {test_loss}')
