%{?scl:%scl_package python-gevent}
%{!?scl:%global pkg_name %{name}}

%global pypi_name gevent

Name:           %{?scl_prefix}python-gevent
Version:        1.2.1
Release:        1%{?dist}
Summary:        Coroutine-based network library

License:        MIT
URL:            http://www.gevent.org/
Source0:        https://files.pythonhosted.org/packages/source/g/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  libevent-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-greenlet} >= 0.4.10

%description
gevent gevent_ is a coroutinebased Python networking library.Features
include:* Fast event loop based on libev_. * Lightweight execution units based
on greenlet_. * Familiar API that reuses concepts from the Python standard
library. * Cooperative sockets with SSL support. * DNS queries performed
through cares_ or a threadpool. * Ability to use standard library and 3rd party
modules

%prep
%global _python_bytecompile_errors_terminate_build 0
%setup -q -n %{pypi_name}-%{version}

%build
%global _python_bytecompile_errors_terminate_build 0
%{?scl:scl enable %{scl} "}
%{__python} setup.py build
%{?scl:"}

%install
%global _python_bytecompile_errors_terminate_build 0
# Explicitly specify --install-purelib %{python_sitelib}, which is now overriden
# to point to vt191, otherwise Python will try to install into the python27
# Software Collection site-packages directory
%{?scl:scl enable %{scl} "}
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib} --install-platlib %{python_sitelib} --install-headers %{python_includedir}
%{?scl:"}
%global _python_bytecompile_errors_terminate_build 0

%files
%{python_sitelib}/%{pypi_name}*
#%{python_includedir}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
