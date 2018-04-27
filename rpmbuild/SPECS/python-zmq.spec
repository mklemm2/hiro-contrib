%{?scl:%scl_package python-zmq}
%{!?scl:%global pkg_name %{name}}

%global pypi_name pyzmq

Name:           %{?scl_prefix}python-zmq
Version:        16.0.2
Release:        1%{?dist}
Summary:        Python bindings for 0MQ

License:        MIT License
URL:            http://www.zeromq.org/
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
BuildRequires:  gcc-c++
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
PyZMQ is the official Python binding for the ZeroMQ
Messaging Library (http://www.zeromq.org).
See the docs for more info.

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
%{python_sitelib}/pyzmq-*
%{python_sitelib}/zmq/*
#%{python_sitelib}/%{pypi_name}*
#%{python_includedir}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
