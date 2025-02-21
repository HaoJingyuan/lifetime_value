import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.distributions as dist

def zero_inflated_lognormal_pred(logits: torch.Tensor) -> torch.Tensor:
    """Calculates predicted mean of zero inflated lognormal logits.

    Arguments:
        logits: [batch_size, 3] tensor of logits.

    Returns:
        preds: [batch_size, 1] tensor of predicted mean.
    """
    logits = logits.float()
    positive_probs = torch.sigmoid(logits[..., :1])
    loc = logits[..., 1:2]
    scale = F.softplus(logits[..., 2:])
    preds = positive_probs * torch.exp(loc + 0.5 * torch.square(scale))
    return preds

def zero_inflated_lognormal_loss(logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    """Computes the zero inflated lognormal loss.

    Usage with PyTorch API:

    ```python
    model = torch.nn.Module(inputs, outputs)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    loss_fn = zero_inflated_lognormal_loss
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = loss_fn(labels, outputs)
        loss.backward()
        optimizer.step()
    ```

    Arguments:
        labels: True targets, tensor of shape [batch_size, 1].
        logits: Logits of output layer, tensor of shape [batch_size, 3].

    Returns:
        Zero inflated lognormal loss value.
    """
    labels = labels.float()
    positive = (labels > 0).float()

    logits = logits.float()
    assert logits.shape == labels.shape[:-1] + (3,)

    positive_logits = logits[..., :1]
    classification_loss = F.binary_cross_entropy_with_logits(positive_logits, positive, reduction='mean')

    loc = logits[..., 1:2]
    scale = F.softplus(logits[..., 2:])
    safe_labels = positive * labels + (1 - positive)
    regression_loss = -torch.mean(positive * dist.LogNormal(loc=loc, scale=scale).log_prob(safe_labels))

    return classification_loss + regression_loss
