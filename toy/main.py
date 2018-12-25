import argparse
from random import randint
from time import sleep
import init_paths

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import os
import pdb

def foo(rank, world_size, steps):
#    print('Inner func foo of rank:{} steps:{} start'.format(rank, steps))
    for step in range(1, steps + 1):
        # get random int
        value = randint(0, 10)
#        print('rank: {}, step: {}/{}, value:{}'.format(rank, step, steps, value))

        # group all ranks
        ranks = list(range(world_size))
        group = dist.new_group(ranks=ranks)
#        print('group get rank: {}, step: {}, value:{}'.format(rank, step, value))

        # compute reduced sum
        tensor = torch.IntTensor([value])
#        print('IntTensor rank: {}, step: {}, value:{}'.format(rank, step, value))
        dist.all_reduce(tensor, op=dist.reduce_op.SUM, group=group)
#        print('all_reduce rank: {}, step: {}, value:{}'.format(rank, step, value))

        print('rank: {}, step: {}, value: {}, reduced sum: {}.'.format(
            rank, step, value, float(tensor)))

#    print('Inner func foo of rank:{} get'.format(rank))
    return 0
#        sleep(1)


def init_process(backend, init_method, rank, world_size):
    dist.init_process_group(
        backend=backend,
        init_method=init_method,
        rank=rank,
        world_size=world_size)
    return 0

def func(backend, init_method, rank, world_size, steps):
    init_process(backend, init_method, rank, world_size)
    foo(rank, world_size, steps)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--backend',
        type=str,
        default='gloo',
        help='Name of the backend to use.')
    parser.add_argument(
        '--init-method',
        '-i',
        type=str,
        default='tcp://127.0.0.1:23456',
        help='URL specifying how to initialize the package.')
    parser.add_argument(
        '--rank', '-r', type=int, default=-1,help='Rank of the current process.')
    parser.add_argument(
        '--world-size',
        '-s',
        type=int,
        default=8,
        help='Number of processes participating in the job.')
    parser.add_argument('--steps', type=int, default=20)
    args = parser.parse_args()
    print(args)

    WAY     = 2
    if WAY == 1:
        # use gloo can run gpu ops, but raise 'terminate called after throwing an instance of 'std::system_error' at all rank end
        if args.rank == -1:
            for r in range(args.world_size):
                cmd_str = './envs/py36/bin/python ./toy/main.py --init-method {} --rank {} --world-size {} --backend {} &'.format(args.init_method, r, args.world_size, args.backend)
                print("Running {}".format(cmd_str))
                os.system(cmd_str)
                print("End {}".format(cmd_str))
        else:
            func(args.backend, args.init_method, args.rank, args.world_size, args.steps)

    elif WAY == 2:
        # use gloo can run
        p   = mp.Pool(args.world_size)
        param_list  = [(args.backend, args.init_method, r, args.world_size, args.steps) for r in range(args.world_size)]
        for ind, param in enumerate(param_list):
            print("index: {} param: {}".format(ind, param))
            p.apply_async(func, args=param)
            print("end index: {} param: {}".format(ind, param))
        print("Waiting for all subprocess end")
        p.close()
        p.join()
        print("All subprocess have end")

#     for param in param_list:
        # # this way must wait for current process terminating, cannot use this
        # p   = mp.Process(target=func, args=param)
        # p.close()
        # p.join()

#    p.map(func, param_list)
#    init_process(args.backend, args.init_method, args.rank, args.world_size)
#    foo(args.rank, args.world_size, args.steps)

if __name__ == '__main__':
    main()
