# puppet-enc
A simple puppet ENC with a YAML file backend. Ideally for
a single puppet master. Able to edit file directly or through
supplied arguments which are detailed below

## Installation
On the puppet master edit `puppet.conf`:

```
    [master]
        node_terminus = exec
        external_nodes = <location_of_enc>/enc.py

```

enc.py will generate a `db.yml` in the relative location
of the script. By default no environments will be set,
this may change later on


##Usage
```
Usage: enc.py [options]

Options:
  -h, --help            show this help message and exit
  -l, --ls
  -r, --rm
  -a, --add
  -e ENVIRONMENT, --env=ENVIRONMENT
  -c CUSTOM, --custom=CUSTOM
  -n NODE, --node=NODE
  -g GROUP, --group=GROUP
  -f FIND, --find=FIND
  ```

enc.py can interact with the db.yml file directly through
supplied arguments. There are 5 direct modes:

* -l or --ls
* -r or --rm
* -a or --add
# -f or --find
* <node_name>

Some of these modes are used in combination with:

* -e or --env
* -n or --node
* -g or --group

##Examples

```
#Add empty environment
enc.py -a --env dbz

#Add node to production environment
enc.py -a --env dbz -n 'dbz-goku.earth.univ'

#Add regex grouping to production environment
enc.py -a --env dbz -g '^dbz'

#Add another node to production environment
enc.py -a -e dbz -n 'dbz-gohan.earth.univ'

#Create another environment
enc.py -a --env dbgt

#Remove the environment and forget it ever happened
enc.py -rm --env dbgt

#Find out which environment dbz-gohan.earth.univ is in
enc.py -f 'dbz-gohan.earth.univ'

#Have puppet find out
enc.py dbz-gohan.earth.univ'

#Add an already supplied environment
enc.py --add --env dbsuper '{"nodes":{"dbsuper-beerus.beerus.univ":""},"groups":{}'

#List specified environmeny
enc.py --ls --env dbsuper

#list all environments
enc.py --ls
```