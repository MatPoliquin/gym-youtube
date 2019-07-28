import numpy as np
from multiprocessing import Array
from ctypes import c_bool
from collections import OrderedDict

from gym import logger
from gym.spaces import Tuple, Dict
from gym.vector.utils.spaces import _BaseGymSpaces

__all__ = [
    'create_shared_memory',
    'read_from_shared_memory',
    'write_to_shared_memory'
]

def create_shared_memory(space, n=1):
    """Create a shared memory object, to be shared across processes. This
    eventually contains the observations from the vectorized environment.

    Parameters
    ----------
    space : `gym.spaces.Space` instance
        Observation space of a single environment in the vectorized environment.

    n : int
        Number of environments in the vectorized environment (i.e. the number
        of processes).

    Returns
    -------
    shared_memory : dict, tuple, or `multiprocessing.Array` instance
        Shared object across processes.
    """
    if isinstance(space, _BaseGymSpaces):
        return create_base_shared_memory(space, n=n)
    elif isinstance(space, Tuple):
        return create_tuple_shared_memory(space, n=n)
    elif isinstance(space, Dict):
        return create_dict_shared_memory(space, n=n)
    else:
        raise NotImplementedError()

def create_base_shared_memory(space, n=1):
    dtype = space.dtype.char
    if dtype in '?':
        dtype = c_bool
    return Array(dtype, n * int(np.prod(space.shape)))

def create_tuple_shared_memory(space, n=1):
    return tuple(create_shared_memory(subspace, n=n)
        for subspace in space.spaces)

def create_dict_shared_memory(space, n=1):
    return OrderedDict([(key, create_shared_memory(subspace, n=n))
        for (key, subspace) in space.spaces.items()])


def read_from_shared_memory(shared_memory, space, n=1):
    """Read the batch of observations from shared memory as a numpy array.

    Parameters
    ----------
    shared_memory : dict, tuple, or `multiprocessing.Array` instance
        Shared object across processes. This contains the observations from the
        vectorized environment. This object is created with `create_shared_memory`.

    space : `gym.spaces.Space` instance
        Observation space of a single environment in the vectorized environment.

    n : int
        Number of environments in the vectorized environment (i.e. the number
        of processes).

    Returns
    -------
    observations : dict, tuple or `np.ndarray` instance
        Batch of observations as a (possibly nested) numpy array.

    Notes
    -----
    The numpy array objects returned by `read_from_shared_memory` shares the
    memory of `shared_memory`. Any changes to `shared_memory` are forwarded
    to `observations`, and vice-versa. To avoid any side-effect, use `np.copy`.
    """
    if isinstance(space, _BaseGymSpaces):
        return read_base_from_shared_memory(shared_memory, space, n=n)
    elif isinstance(space, Tuple):
        return read_tuple_from_shared_memory(shared_memory, space, n=n)
    elif isinstance(space, Dict):
        return read_dict_from_shared_memory(shared_memory, space, n=n)
    else:
        raise NotImplementedError()

def read_base_from_shared_memory(shared_memory, space, n=1):
    return np.frombuffer(shared_memory.get_obj(),
        dtype=space.dtype).reshape((n,) + space.shape)

def read_tuple_from_shared_memory(shared_memory, space, n=1):
    return tuple(read_from_shared_memory(memory, subspace, n=n)
        for (memory, subspace) in zip(shared_memory, space.spaces))

def read_dict_from_shared_memory(shared_memory, space, n=1):
    return OrderedDict([(key, read_from_shared_memory(memory, subspace, n=n))
        for ((key, memory), subspace) in zip(shared_memory.items(), 
        space.spaces.values())])


def write_to_shared_memory(index, value, shared_memory, space):
    """Write the observation of a single environment into shared memory.

    Parameters
    ----------
    index : int
        Index of the environment (must be in `[0, num_envs)`).

    value : sample from `space`
        Observation of the single environment to write to shared memory.

    shared_memory : dict, tuple, or `multiprocessing.Array` instance
        Shared object across processes. This contains the observations from the
        vectorized environment. This object is created with `create_shared_memory`.

    space : `gym.spaces.Space` instance
        Observation space of a single environment in the vectorized environment.

    Returns
    -------
    `None`
    """
    if isinstance(space, _BaseGymSpaces):
        write_base_to_shared_memory(index, value, shared_memory, space)
    elif isinstance(space, Tuple):
        write_tuple_to_shared_memory(index, value, shared_memory, space)
    elif isinstance(space, Dict):
        write_dict_to_shared_memory(index, value, shared_memory, space)
    else:
        raise NotImplementedError()

def write_base_to_shared_memory(index, value, shared_memory, space):
    size = int(np.prod(space.shape))
    shared_memory[index * size:(index + 1) * size] = np.asarray(value,
        dtype=space.dtype).flatten()

def write_tuple_to_shared_memory(index, values, shared_memory, space):
    for value, memory, subspace in zip(values, shared_memory, space.spaces):
        write_to_shared_memory(index, value, memory, subspace)

def write_dict_to_shared_memory(index, values, shared_memory, space):
    for key, value in values.items():
        write_to_shared_memory(index, value, shared_memory[key], space.spaces[key])
