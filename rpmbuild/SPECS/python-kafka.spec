%{?scl:%scl_package python-kafka}
%{!?scl:%global pkg_name %{name}}

%global pypi_name kafka

Name:           %{?scl_prefix}python-kafka
Version:        1.3.3
Release:        1%{?dist}
Summary:        Python client for the Apache Kafka distributed stream processing system.

License:        Apache
URL:            https://github.com/dpkp/kafka-python
Source0:        https://files.pythonhosted.org/packages/source/k/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
#BuildRequires:  gcc
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
Python client for the Apache Kafka distributed stream processing system. kafka-python is designed to function much like the official java client, with a sprinkling of pythonic interfaces (e.g., consumer iterators).

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
%{python_sitelib}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
