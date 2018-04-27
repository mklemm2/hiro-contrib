%{?scl:%scl_package python-cython}
%{!?scl:%global pkg_name %{name}}

%global pypi_name cython

Name:           %{?scl_prefix}python-cython
Version:        0.25.2
Release:        1%{?dist}
Summary:        The Cython compiler for writing C extensions for the Python language.

License:        Apache
URL:            http://cython.org
Source0:        https://files.pythonhosted.org/packages/source/c/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
The Cython language makes writing C extensions for the
Python language as easy as Python itself. Cython is a
source code translator based on Pyrex, but supports
more cutting edge functionality and optimizations.

The Cython language is a superset of the Python
language (almost all Python code is also valid Cython
code), but Cython additionally supports optional static
typing to natively call C functions, operate with C++
classes and declare fast C types on variables and class
attributes. This allows the compiler to generate very
efficient C code from Cython code.

This makes Cython the ideal language for writing glue
code for external C/C++ libraries, and for fast C
modules that speed up the execution of Python code.

%prep
%setup -q -n %{pypi_name}-%{version}

%build
%{?scl:scl enable %{scl} "}
%{__python} setup.py build
%{?scl:"}

%install
# Explicitly specify --install-purelib %{python_sitelib}, which is now overriden
# to point to vt191, otherwise Python will try to install into the python27
# Software Collection site-packages directory
%{?scl:scl enable %{scl} "}
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib} --install-platlib %{python_sitelib} --install-headers %{python_includedir}
%{?scl:"}

%files
%{python_sitelib}/Cython/*
%{python_sitelib}/pyximport/*
%{python_sitelib}/cython.py
%{python_sitelib}/Cython-*
%{python_sitelib}/__pycache__/*
/opt/rh/rh-python34/root/usr/bin/cygdb
/opt/rh/rh-python34/root/usr/bin/cython
/opt/rh/rh-python34/root/usr/bin/cythonize

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
