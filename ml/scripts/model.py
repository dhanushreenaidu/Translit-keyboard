import torch
import torch.nn as nn


class Encoder(nn.Module):
    def __init__(self, vocab_size: int, emb_dim: int, hid_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.rnn = nn.LSTM(
            emb_dim,
            hid_dim,
            batch_first=True,
            bidirectional=True,
        )

    def forward(self, src: torch.Tensor):
        """
        src: (batch, src_len)
        returns:
          encoder_outputs: (batch, src_len, hid_dim * 2)
          hidden: (1, batch, hid_dim)
          cell:   (1, batch, hid_dim)
        """
        embedded = self.embedding(src)  # (batch, src_len, emb_dim)
        outputs, (hidden, cell) = self.rnn(embedded)
        # hidden, cell: (2, batch, hid_dim) -> fw + bw
        hidden = hidden[0] + hidden[1]  # (batch, hid_dim)
        cell = cell[0] + cell[1]  # (batch, hid_dim)

        hidden = hidden.unsqueeze(0)  # (1, batch, hid_dim)
        cell = cell.unsqueeze(0)  # (1, batch, hid_dim)

        return outputs, hidden, cell


class Attention(nn.Module):
    def __init__(self, hid_dim: int):
        super().__init__()
        # encoder_outputs: (batch, src_len, hid_dim*2)
        # hidden (for attn): (batch, hid_dim)
        self.attn = nn.Linear(hid_dim * 3, hid_dim)
        self.v = nn.Linear(hid_dim, 1, bias=False)

    def forward(self, hidden: torch.Tensor, encoder_outputs: torch.Tensor):
        """
        hidden: (1, batch, hid_dim)
        encoder_outputs: (batch, src_len, hid_dim*2)
        returns:
          attn_weights: (batch, src_len)
        """
        # last layer hidden -> (batch, hid_dim)
        hidden = hidden[-1]

        batch_size = encoder_outputs.size(0)
        src_len = encoder_outputs.size(1)

        # repeat hidden src_len times: (batch, src_len, hid_dim)
        hidden_expanded = hidden.unsqueeze(1).repeat(1, src_len, 1)

        energy = torch.tanh(
            self.attn(torch.cat((hidden_expanded, encoder_outputs), dim=2))
        )  # (batch, src_len, hid_dim)

        # project to scalar
        attention = self.v(energy).squeeze(2)  # (batch, src_len)

        return torch.softmax(attention, dim=1)


class Decoder(nn.Module):
    def __init__(
        self, vocab_size: int, emb_dim: int, hid_dim: int, attention: Attention
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.attention = attention
        self.rnn = nn.LSTM(
            hid_dim * 2 + emb_dim,
            hid_dim,
            batch_first=True,
        )
        self.fc_out = nn.Linear(hid_dim * 3 + emb_dim, vocab_size)

    def forward(
        self,
        input: torch.Tensor,
        hidden: torch.Tensor,
        cell: torch.Tensor,
        encoder_outputs: torch.Tensor,
    ):
        """
        input: (batch,)
        hidden: (1, batch, hid_dim)
        cell:   (1, batch, hid_dim)
        encoder_outputs: (batch, src_len, hid_dim*2)
        """
        # input -> (batch, 1)
        input = input.unsqueeze(1)
        embedded = self.embedding(input)  # (batch, 1, emb_dim)

        attn_weights = self.attention(hidden, encoder_outputs)  # (batch, src_len)
        attn_weights = attn_weights.unsqueeze(1)  # (batch, 1, src_len)

        context = torch.bmm(attn_weights, encoder_outputs)  # (batch, 1, hid_dim*2)

        rnn_input = torch.cat(
            (embedded, context), dim=2
        )  # (batch, 1, emb_dim+hid_dim*2)

        output, (hidden, cell) = self.rnn(rnn_input, (hidden, cell))
        # output: (batch, 1, hid_dim)
        output = output.squeeze(1)  # (batch, hid_dim)
        embedded = embedded.squeeze(1)  # (batch, emb_dim)
        context = context.squeeze(1)  # (batch, hid_dim*2)

        pred_input = torch.cat(
            (output, context, embedded), dim=1
        )  # (batch, hid_dim*3+emb_dim)
        prediction = self.fc_out(pred_input)  # (batch, vocab_size)

        return prediction, hidden, cell


class Seq2Seq(nn.Module):
    def __init__(self, encoder: Encoder, decoder: Decoder, device: torch.device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device

    def forward(self, src: torch.Tensor, trg: torch.Tensor):
        """
        src: (batch, src_len)
        trg: (batch, trg_len)
        returns:
          outputs: (batch, trg_len-1, vocab_size)
        """
        encoder_outputs, hidden, cell = self.encoder(src)

        batch_size = src.size(0)
        trg_len = trg.size(1)
        vocab_size = self.decoder.fc_out.out_features

        outputs = torch.zeros(batch_size, trg_len - 1, vocab_size, device=self.device)

        # first decoder input = <sos>
        input = trg[:, 0]  # (batch,)

        for t in range(1, trg_len):
            output, hidden, cell = self.decoder(input, hidden, cell, encoder_outputs)
            outputs[:, t - 1, :] = output
            # teacher forcing: next input = next token in target
            input = trg[:, t]

        return outputs
