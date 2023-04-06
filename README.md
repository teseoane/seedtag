Seedtag Codetest 2: Backend Engineer
====================================


## Running local environment

### Build the image
```bash
docker build -t python/seedtag:version1.0 .
```

### Run a container based on the image
```bash
docker run -d --name seedtag -p 8888:8888 python/seedtag:version1.0
```
