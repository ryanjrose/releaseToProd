# releaseToProd.py

releaseToProd.py is a simple, configurable script to push code to multiple servers and environments

### Why?
- Improve deployment speed
- Limit pilot errors
- Minimize workflow; Consolidate multiple steps into one
- Creates consistent, repeatable environment

### Install
> Note: Although releaseToProd depends on just two modules, You are encouraged to use [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to isolate Python 
> and required modules.

```
$ pip install -r requirements.txt
```

### Config

Configuration files are [YAML](http://yaml.org/) files!

By default, releaseToProd.py will look for a file named _config.yaml_.  
You may specify your own file with the --config option.

A config file will contain at a minimum a source path and a destination path.





---
**Minimal config.yaml**

*This config will do nothing more than rsync files from the source path to the destination*
```
---                                                                                                                                                                                                                      
/source/path/  user@host:/remote/path/: ~                                                                                                                                                  
```
---
**Typical config.yaml**

A more typical config file will look like the following:
*Typical config.yaml*
```
---                                                                                                                                                                                                                      
/source/path/  user@host:/remote/path/:                                                                                                                                                  
  excludeFiles:                                                                                                                                                                                                          
    - '*.swp'
  postProcess:
    - "ssh root@10.20.242 'chown -R nodeuser.root /remote/path/*'"
```

--
**Advanced config.yaml**

But, you can specify any number of source/destination blocks within the same config file, each with their own post proceses and exclusion list:
```
---
/source/path/  user@server-A:/remote/path/:
  excludeFiles:
    - 'logs'
    - '*.swp'
    - '.git'
  postProcess: 
    - "ssh root@10.100.0.1 '/usr/local/bin/empty_cache'"
    - "echo 'Sync Complete' > ~/status.log"
/source/path/  user@server-B:/remote/path/:
  excludeFiles: 
    - '.git'
  postProcess: ~
/source/path/  user@server-C:/remote/path/: ~
```


By default, releaseToProd.py looks file the file _config.yaml_

## Run
> Note: It's advisable to copy your ssh public key to each destination host's authorize_keys file

```
    Usage:
        releaseToProd.py  [options]

    Options:
        -h --help       Show this screen.

        -v --version    Show version.

        -d --dry        Does not actually push code; Just show the files that would be pushed.

        -c --config	YAML config file specifying source and target paths for code push
```
Running is as simple as:
```
$ ./releaseToProd.py --config staging.yaml
```
