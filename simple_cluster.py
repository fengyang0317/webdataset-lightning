# -*- Python -*-

#
# Copyright (c) 2017-2023 NVIDIA CORPORATION. All rights reserved.
# This file is part of the WebDataset library.
# See the LICENSE file for licensing terms (BSD-style).
#

# A simple example of using WebDataset high performance distributed storage
# for ImageNet training.  This uses the PyTorch Lightning framework.

# Loosely based on
# https://github.com/PyTorchLightning/pytorch-lightning/blob/master/pl_examples/domain_templates/imagenet.py

import functools
import pytorch_lightning as pl
import os

class SimpleCluster(pl.plugins.environments.ClusterEnvironment):
    def __init__(self):
        super().__init__()

    def creates_children(self) -> bool:
        return True

    # actual cluster configuration

    def master_address(self) -> str:
        return os.environ["MASTER_ADDR"]

    def master_port(self) -> int:
        return int(os.environ.get("MASTER_PORT", 25666))

    def world_size(self) -> int:
        return int(os.environ["WORLD_SIZE"])

    def global_rank(self) -> int:
        return int(os.environ["RANK"])

    # these have been disabled

    def set_world_size(self, size: int) -> None:
        if size != self.world_size():
            print(f"set_world_size ignored wants: {size} gets: {self.world_size()}")

    def set_global_rank(self, rank: int) -> None:
        if rank != self.global_rank():
            print(f"set_global_rank ignored wants: {rank} gets: {self.global_rank()}")

    # cluster structure information

    def local_rank(self) -> int:
        return 0

    def node_rank(self) -> int:
        return int(os.environ["RANK"])


def debug_nccl():
    os.environ["NCCL_DEBUG"] = "INFO"
    os.environ["NCCL_DEBUG_SUBSYS"] = "COLL"


def auto_configure_nccl():
    os.environ["NCCL_IB_DISABLE"] = "1"
    if "NCCL_SOCKET_IFNAME" not in os.environ:
        mainif = os.popen("""/sbin/route -n | awk '$1=="0.0.0.0"{print $8; exit}'""").read().strip()
        os.environ["NCCL_SOCKET_IFNAME"] = mainif
    print(f"setting NCCL_SOCKET_IFNAME to {mainif}")

def itrace(f):
    @functools.wraps(f)
    def g(*args, **kw):
        result = f(*args, **kw)
        print(f"{f.__name__}({args}, {kw}) => {result}")
        return result
    return g
