from aocd import get_data # type: ignore
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union, List, Tuple

class FileSystemObject:
    pass

class Directory(FileSystemObject):

    def __init__(self, name: str, parent: 'Directory'):
        self.name = name
        self.totsize = 0
        self.parent = parent
        self.children: List[FileSystemObject] = []
        self.is_dir = True

class File(FileSystemObject):

    def __init__(self, name: str, size: int, parent: Directory):
        self.name = name
        self.size = size
        self.parent = parent
        self.is_dir = False


class ReaderState(Enum):
    COMMAND = 0
    LISTINGDIR = 1
    LISTINGFILE = 2

class Command(Enum):
    LIST = 0
    CHANGEDIR = 1


def build_filesystem(data: str) -> List[FileSystemObject]:
    root = workingdir = Directory('/', parent=None)
    readstate = ReaderState.COMMAND
    lines = iter(data.split('\n'))

    next(lines) # First command of `cd /` can be discarded.`

    for line in lines:
        if line.startswith('$'):
            readstate = ReaderState.COMMAND
            command, arg = parse_command(line)
        elif line.startswith('dir'):
            readstate = ReaderState.LISTINGDIR
            name = parse_directory_listing(line)
        else:
            readstate = ReaderState.LISTINGFILE
            size, name = parse_file_listing(line)

        if readstate == ReaderState.COMMAND and command == Command.CHANGEDIR:
            if arg == '..':
                workingdir = workingdir.parent
                continue
            workingdir = next(
                obj for obj in workingdir.children
                if obj.is_dir and obj.name == arg
            )
        elif readstate == ReaderState.COMMAND and command == Command.LIST:
                continue
        elif readstate == ReaderState.LISTINGDIR:
            newdir = Directory(name=name, parent=workingdir)
            workingdir.children.append(newdir)
        elif readstate == ReaderState.LISTINGFILE:
            newfile = File(name=name, size=int(size), parent=workingdir)
            workingdir.children.append(newfile)

    return root

def parse_command(line: str) -> Tuple[Command, str]:
    command = line[2:]  # line = '$ the part we care about'
    if command.startswith('ls'):
        return Command.LIST, ''
    elif command.startswith('cd'):
        _, name = command.split(' ')
        return Command.CHANGEDIR, name.strip()
    else:
        raise ValueError(f"Unknown command in line {line}")

def parse_directory_listing(line: str) -> str:
    return line[4:].strip()  # line = 'dir dirname'

def parse_file_listing(line: str) -> Tuple[int, str]:
    size, name = line.split(' ')
    return int(size.strip()), name.strip()

def accumulate_filesizes(dir: Directory) -> int:
    totsize = 0
    for obj in dir.children:
        if obj.is_dir:
            totsize += accumulate_filesizes(obj)
        else:
            totsize += obj.size
    dir.totsize = totsize
    return totsize

def find_all_subdirectories(dir: Directory, maxsize: int=0) -> List[Directory]:
    subdirectories = [dir]
    for obj in dir.children:
        if obj.is_dir:
            subdirectories.extend(find_all_subdirectories(obj))
    return subdirectories


if __name__ == '__main__':
    data = get_data(day=7, year=2022)

    root = build_filesystem(data)
    USED_SPACE = accumulate_filesizes(root)
    DIRS = find_all_subdirectories(root)

    smoldirs = [dir for dir in DIRS if dir.totsize <= 100_000]
    smolsize = sum(dir.totsize for dir in smoldirs)
    print(f"The total size of all smol directories is {smolsize}")

    TOTAL_SPACE = 70_000_000
    NEED_SPACE = 30_000_000
    FREE_SPACE = TOTAL_SPACE - USED_SPACE
    MIN_FREE = NEED_SPACE - FREE_SPACE
    print(f"We need to free at least {MIN_FREE}")

    sufficientdirs = [dir for dir in DIRS if dir.totsize >= MIN_FREE]
    thedir = min(sufficientdirs, key=lambda dir: dir.totsize)
    print(f"Deleting directory {thedir.name} of total size {thedir.totsize} is optimal.")
