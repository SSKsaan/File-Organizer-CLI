# File-Organizer-CLI
A single-file project demonstrating OOP concept using Python in a simple CLI-based File Organizer tool.

## Run
```bash
python file-organizer-oop.py
```
No external dependencies — standard library only.

## What it does
Moves files in a given folder into categorized subfolders (Images, Documents, Videos, etc.).

## OOP Concepts Demonstrated
| Concept | Where |
|---|---|
| Encapsulation | `FileItem` hides extension parsing |
| Abstraction | `BaseRule` defines the rule interface, `FileManager` hides file system calls |
| Inheritance | `DefaultRule` implements `BaseRule` |
| Polymorphism | `CustomRule` and `FilterRule` override `get_category` differently |
