import torch
import torch.nn as nn
import math
from torch.autograd import Variable
import torch.nn.functional as F

# Necessary for my KFAC implementation.
class AddBias(nn.Module):
    def __init__(self, bias):
        super(AddBias, self).__init__()
        self._bias = nn.Parameter(bias.unsqueeze(1))

    def forward(self, x):
        if x.dim() == 2:
            bias = self._bias.t().view(1, -1)
        else:
            bias = self._bias.t().view(1, -1, 1, 1)

        return x + bias
class att(nn.Module):
    def __init__(self, hidden_in, hidden_out):
        super(att, self).__init__()
        self.hidden_in = hidden_in
        self.hidden_out = hidden_out
        self.context_att = nn.Linear(self.hidden_in, self.hidden_out)
        self.hidden_att = nn.Linear(self.hidden_out, self.hidden_out, bias=False) # NO BIAS
        self.joint_att = nn.Linear(self.hidden_out, 1)
        self.softmax = nn.Softmax(dim=1)


    def forward(self, contexts, hidden):
        #print(contexts.size(), hidden.size(), "IN THE FORWARD GUY")
        ##################### -- CONTEXT ENCODED-- ########################
        #print(contexts.size())
        c = self.context_att(contexts)
        #print(c.size(), "THIS IS THE SIZE OF THE CONTEXT GUY")

        ###################################################################
        #----------------------------------------------------------------#
        ##################### -- HIDDEN ENCODED -- ######################
        #print(hidden.size(), "THE HIDDEN INSIDE ATTENTION")
        h = self.hidden_att(hidden)
        h = h.unsqueeze(1)
        #print("BEFORE REPEAT",h.size())
        h = h.repeat(1, 49, 1)
        #print(h.size(), "THIS IS THE SIZE OF THE HIDDEN GUY")
        #h = h.expand(49, 512)
        ###############################################################
        #print(c.size(), h.size())
        final = c + h
        final = F.tanh(final)

        alpha = self.joint_att(final)
        #print(alpha.size())
        alpha = alpha.squeeze(2)
        #print(alpha)
        alpha = self.softmax(alpha)
        #print("THIS IS FINAL", final.size(), "THIS IS alpha", alpha.size(), "AND THIS IS THE CONTEXT", contexts.size())
        alpha = alpha.unsqueeze(2)
        weighted_context = torch.sum((alpha * contexts), 1)
        #print("SHIIIITI I FINISHED ?????????????????",weighted_context.size())
        return weighted_context



"""class att(nn.Module):
    def __init__(self, method, hidden_size):
        super(att, self).__init__()
        self.method = method
        self.hidden_size = hidden_size
        self.attn = nn.Linear(self.hidden_size * 2, hidden_size)
        self.v = nn.Parameter(torch.rand(hidden_size))
        # update: initalizing with torch.rand is not a good idea
        # Better practice is to initialize with zero mean and 1/sqrt(n) standard deviation
        stdv = 1. / math.sqrt(self.v.size(0))
        self.v.data.uniform_(-stdv, stdv)
        # end of update
        self.softmax = nn.Softmax()
        self.USE_CUDA = False


    def forward(self, hidden, encoder_outputs):
        '''
        :param hidden:
            previous hidden state of the decoder, in shape (layers*directions,B,H)
        :param encoder_outputs:
            encoder outputs from Encoder, in shape (T,B,H)
        :return
            attention energies in shape (B,T)
        '''
        max_len = encoder_outputs.size(0)
        this_batch_size = encoder_outputs.size(1)
        # For storing attention energies
        attn_energies = Variable(torch.zeros(this_batch_size, max_len))
        if self.USE_CUDA:
            attn_energies = attn_energies.cuda()
        H = hidden.repeat(max_len,1,1).transpose(0,1)
        encoder_outputs = encoder_outputs.transpose(0,1) # [B*T*H]
        attn_energies = self.score(H,encoder_outputs) # compute attention score
        return self.softmax(attn_energies).unsqueeze(1) # normalize with softmax

    def score(self, hidden, encoder_outputs):
        energy = self.attn(torch.cat([hidden, encoder_outputs], 2)) # [B*T*2H]->[B*T*H]
        energy = energy.transpose(2,1) # [B*H*T]
        v = self.v.repeat(encoder_outputs.data.shape[0],1).unsqueeze(1) #[B*1*H]
        energy = torch.bmm(v,energy) # [B*1*T]
        return energy.squeeze(1) #[B*T]"""

# A temporary solution from the master branch.
# https://github.com/pytorch/pytorch/blob/7752fe5d4e50052b3b0bbc9109e599f8157febc0/torch/nn/init.py#L312
# Remove after the next version of PyTorch gets release.
def orthogonal(tensor, gain=1):
    if tensor.ndimension() < 2:
        raise ValueError("Only tensors with 2 or more dimensions are supported")

    rows = tensor.size(0)
    cols = tensor[0].numel()
    flattened = torch.Tensor(rows, cols).normal_(0, 1)

    if rows < cols:
        flattened.t_()

    # Compute the qr factorization
    q, r = torch.qr(flattened)
    # Make Q uniform according to https://arxiv.org/pdf/math-ph/0609050.pdf
    d = torch.diag(r, 0)
    ph = d.sign()
    q *= ph.expand_as(q)

    if rows < cols:
        q.t_()

    tensor.view_as(q).copy_(q)
    tensor.mul_(gain)
    return tensor

def where(cond, x_1, x_2):
    return (cond * x_1) + ((1-cond) * x_2)

def maxout(input, k=2):
    shape = input.size()
    #print(shape)
    if len(shape) == 2:
        #print("FULLY CONNECTED MAXOUT")
        x = input.view(shape[0], k, shape[1]//k)
    elif len(shape) == 3 or len(shape) == 4:
        #print("CONVOLUTION MAXOUT")
        x = input.view(shape[0], k, shape[1]//k, shape[2], shape[3])

    x, x_ind = torch.max(x, dim=1)
    #print(x)
    return x

def lwta(input, k=2):
    shape = input.size()
    #print(shape)
    x = input.clone()
    if len(shape) == 2:
        #print("FULLY CONNECTED MAXOUT")
        x = x.view(shape[0], k, shape[1]//k)
    elif len(shape) == 3 or len(shape) == 4:
        #print("CONVOLUTION MAXOUT")
        x = x.view(shape[0], k, shape[1]//k, shape[2], shape[3])

    #print(x[0,1, 0], x[0,0, 0])
    #print(x.size(), "BEFORE MAX")
    _, x_ind = torch.max(x, dim=1)
    #print(x_ind)
    if torch.cuda.is_available():
        mask = torch.zeros(x.size()).cuda()

    mask = mask.view(shape[0], k, -1)
    x_ind = x_ind.view(shape[0], -1)

    #print(x_ind.size(), "INDEX SIZE")
    #print(mask.size(), "MASK SIZE")


    for i in range(x_ind.size(0)):
        for ind in range(x_ind.size(1)):
            mask[i, x_ind.data[i, ind], ind] = 1.0

    #print(mask)
    x = x.view(shape[0], k, -1)

    #print(x.data[0,0, :5].numpy(), "BEFORE MAX")
    #print(x.data[0,1, :5].numpy(), "BEFORE MAX")
    x = x.data * mask
    #print(x[0, 0,:5].numpy(), "AFTER MAX")
    #print(x[0, 1,:5].numpy(), "AFTER MAX")

    x = x.view(shape[0], shape[1], shape[2], shape[3])
    return Variable(x)
