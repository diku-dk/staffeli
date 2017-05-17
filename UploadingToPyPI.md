```
python3 setup.py sdist
gpg2 --detach-sign -a dist/staffeli-<version>.tar.gz
twine upload dist/staffeli-<version>.tar.gz*  # tar.gz and tar.gz.asc
```
