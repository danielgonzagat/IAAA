from lemnisiana.adapters.NeuromodulatedNetwork import NeuromodulatedNetwork
from lemnisiana.modules.ednag.stub import propose
from lemnisiana.modules.backpropamine.stub import train

def test_ednag_propose():
    cands = propose(2)
    assert len(cands) == 2
    assert "fitness" in cands[0]

def test_backpropamine_train():
    out = train(steps=5)
    assert out["loss_end"] < out["loss_start"]
    assert out["stable"] is True

def test_neuromod_net_interface():
    net = NeuromodulatedNetwork(beta=0.1)
    stats = net.train_step(batch=[1,2,3])
    assert "loss" in stats and "stable" in stats
