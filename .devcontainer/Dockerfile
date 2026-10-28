# The Python dev container image ships a Yarn apt source whose signing key is no longer valid, so
# every `apt-get update`, including the docker-in-docker feature's install, fails. FORGE-0 doesn't
# use Yarn: drop the source before the features are installed on top of this image.
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
RUN rm -f /etc/apt/sources.list.d/yarn*
