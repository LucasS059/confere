"""Transformer causal pequeno; todos os pesos começam aleatórios."""

from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F


@dataclass
class GPTConfig:
    vocab_size: int
    block_size: int = 1024
    width: int = 384
    layers: int = 6
    heads: int = 6

    def __post_init__(self):
        if min(self.vocab_size, self.block_size, self.width, self.layers, self.heads) <= 0 or self.width % self.heads:
            raise ValueError("Dimensões devem ser positivas e width deve ser divisível por heads.")


class Block(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.heads = config.heads
        self.norm1 = nn.LayerNorm(config.width)
        self.qkv = nn.Linear(config.width, 3 * config.width)
        self.projection = nn.Linear(config.width, config.width)
        self.norm2 = nn.LayerNorm(config.width)
        self.mlp = nn.Sequential(nn.Linear(config.width, 4 * config.width), nn.GELU(), nn.Linear(4 * config.width, config.width))

    def forward(self, x):
        batch, length, width = x.shape
        q, k, v = [item.view(batch, length, self.heads, width // self.heads).transpose(1, 2) for item in self.qkv(self.norm1(x)).chunk(3, dim=-1)]
        attended = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=0.0)
        x = x + self.projection(attended.transpose(1, 2).contiguous().view(batch, length, width))
        return x + self.mlp(self.norm2(x))


class GPT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.width)
        self.position_embedding = nn.Embedding(config.block_size, config.width)
        self.blocks = nn.Sequential(*(Block(config) for _ in range(config.layers)))
        self.norm = nn.LayerNorm(config.width)
        self.head = nn.Linear(config.width, config.vocab_size, bias=False)
        self.apply(self.initialize)

    @staticmethod
    def initialize(module):
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, ids):
        if ids.ndim != 2 or not 0 < ids.shape[1] <= self.config.block_size:
            raise ValueError("Sequência vazia ou maior que a janela de contexto.")
        positions = torch.arange(ids.shape[1], device=ids.device)
        x = self.token_embedding(ids) + self.position_embedding(positions)
        return self.head(self.norm(self.blocks(x)))

    def load_local_checkpoint(self, checkpoint, extend_context=False):
        source=GPTConfig(**checkpoint["config"])
        for name in ("vocab_size","width","layers","heads"):
            if getattr(source,name)!=getattr(self.config,name):
                raise ValueError("Arquitetura/tokenizer incompatíveis com o checkpoint.")
        weights=dict(checkpoint["model"])
        if source.block_size!=self.config.block_size:
            if not extend_context or source.block_size>self.config.block_size:
                raise ValueError("Mudança de contexto exige expansão explícita.")
            positions=self.position_embedding.weight.detach().clone()
            positions[:source.block_size]=weights["position_embedding.weight"].to(positions.device)
            weights["position_embedding.weight"]=positions
        self.load_state_dict(weights)

    @torch.no_grad()
    def generate(self, prompt, max_new_tokens, eos, on_token=None, should_stop=None):
        if prompt.shape[1] + max_new_tokens > self.config.block_size:
            raise ValueError("Prompt e geração excedem o contexto; não há truncamento silencioso.")
        for _ in range(max_new_tokens):
            if should_stop is not None and should_stop():
                break
            next_id = self(prompt)[:, -1].argmax(dim=-1, keepdim=True)
            prompt = torch.cat((prompt, next_id), dim=1)
            if on_token is not None:
                on_token(next_id.item())
            if next_id.item() == eos:
                break
        return prompt
