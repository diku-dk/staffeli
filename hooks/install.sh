#!/usr/bin/env bash

# Copyright (c) 2016-2017 Oleks <oleks@oleks.info>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

set -euo pipefail

script_dir="$(cd "$(dirname "${0}")" && pwd -P)"

install_dir=${script_dir}/../.git/hooks/

# Install by symlinking the files here. The files may already exist, and may
# already point to here. install_file() attempts to account for these cases.

# install_file is run as a subprocess to report all errors (i.e., installations
# are deemed independent). Hence, install_file is wrapped in (), not mere {}.

function install_file() (
  file=${1}
  dest_path="${install_dir}/${file}"
  orig_path="${script_dir}/${file}"

  if [ -f "${dest_path}" ]; then
    if [ "${dest_path}" != "${orig_path}" ]; then
      echo "${install_dir} already has a file ${file}."
      exit 1
    else
      # Already installed
      exit 0
    fi
  fi
  ln -s "${orig_path}" "${dest_path}"
)

function install_files {
  while [ $# -gt 0 ]; do
    install_file $1
    shift
  done
}

install_files \
  pre-commit
