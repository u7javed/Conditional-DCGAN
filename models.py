import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import torch

'''Discriminator'''
class Discriminator(nn.Module):
    def __init__(self, label_size):
        super(Discriminator, self).__init__()
        #label = [B]
        self.embedding = nn.Embedding(label_size, 4*28*28)
        #label after embed = [B, 4*28*28]
        self.label_conv = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=(4, 4), stride=2, padding = 1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True)
        )

        self.image_conv = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=(3, 3), stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True)
        )

        #input shape: [B, 1, 28, 28]
        self.pred = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=(4, 4), stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(256, 512, kernel_size=(4, 4), stride=2, padding=1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(512, 1024, kernel_size=(4, 4), stride=2, padding=2),
            nn.BatchNorm2d(1024),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(1024, 1, kernel_size=(4, 4), stride=1, padding=0),
            nn.Sigmoid()

        )

    def forward(self, x, labels):
        labels = self.embedding(labels)
        labels = labels.view(labels.size(0), 1, 56, 56) #[B, 1, 56, 56]
        labels = self.label_conv(labels)

        #x = [B, 1, 24, 24]
        x = self.image_conv(x)

        x = torch.cat([x, labels], 1)
        x = self.pred(x)
        return x


'''Generator'''
class Generator(nn.Module):
    def __init__(self, label_size, embedding_dim, latent_size=100):
        super(Generator, self).__init__()

        self.embedding = nn.Embedding(label_size, embedding_dim)
        #input image shape(B,C,H,W) = [B, latent_size + embedding_dim, 1, 1]
        self.conv = nn.Sequential(
            nn.ConvTranspose2d(latent_size + embedding_dim, 1024, kernel_size=(4, 4), stride=2, padding=1),
            nn.BatchNorm2d(1024),
            nn.ReLU(inplace=True),
            #result: [B, 50, 2, 2]

            nn.ConvTranspose2d(1024, 512, kernel_size=(4, 4), stride=2, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            #result: [B, 30, 4, 4]

            nn.ConvTranspose2d(512, 256, kernel_size=(4, 4), stride=1, padding=0),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            #result: [B, 15, 7, 7]

            nn.ConvTranspose2d(256, 128, kernel_size=(4, 4), stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            #result: [B, 8, 14, 14]

            nn.ConvTranspose2d(128, 1, kernel_size=(4, 4), stride=2, padding=1),
            nn.Tanh()
            #result: [B, 1, 28, 28]
        )

    def forward(self, x, labels):
        #x = [B, latent_size]
        labels = self.embedding(labels)
        #labels after embedding = [B, embedding_dim]
        x = torch.cat([x, labels], 1)
        x = x.view(x.size(0), -1, 1, 1) # = [B, latent_size + embedding_dim, 1, 1]
        return self.conv(x)