# Aube

Aube stands for *Autonomous Universal Blissful rEgistration*.

## About Aube

Aube is a network managing software forked from [Re2o](http://gitlab.federez.net/federez/re2o) developed initially by [Rézo Metz](https://rezometz.org/) and [other FedeRez volunteers](https://federez.net/).
It enables people to subscribe to a membership and to manage their network devices.

This software is licensed under the *GNU public license v2.0*.

## Philosophy

This software targets student networks that needs to manage a large amount of
members and devices.

Although it has not been the case from the start, we try to follow as much as possible principles such as [KISS](https://en.wikipedia.org/wiki/KISS_principle) and [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).

We chose the **Django Framework** with a **Python 3** environment because it follows these principles without having a steep learning curve.

## How Aube is different from Re2o

Re2o had been developed with the idea of simple migrations, but the base structure make is untenable in the long term. So there was a need to fork and break things a bit to switch to a cleaner structure. **So do expect some bug if you upgrade from Re2o to Aube!**

What have been done so far in Aube that is not in Re2o :

  * Dropped all dead branches ;
  * Switched to SPDX license identifiers to have lighter source files ;
  * Reset Re2o migrations ;
  * Update to Django 1.11 LTS ;
  * Port to Debian Buster dependencies ;
  * Create Docker container configuration ;
  * Dynamic menu, automatically populated depending on permissions and activated apps ;
  * Add automatic documentation with Django AdminDocs ;
  * More coming soon…

## How to migrate from Re2o to Aube

To migrate from Re2o, please go to commit
`f69c88d8fe14546f33ceb1e4e2adbea85a0b5de3` on Re2o dev branche,
make new migrations, migrate data, then switch to Aube.

## How to develop

## With Docker

There is a Dockerfile to contain Aube. You can build it and run it with :

```bash
docker build -t aube .
docker run -d -p 8080:8080 -v /absolute/path/to/aube:/var/www/aube --restart=always aube
```

To stop it :

```bash
docker ps
docker stop container_name
docker container prune
```

