%{?scl:%scl_package python-arago-pyconnectit-common-rest-plugins-base}
%{!?scl:%global pkg_name %{name}}

%global pypi_name arago-pyconnectit-common-rest-plugins-base
%{!?rel:%global rel 1}

Name:           %{?scl_prefix}python-%{pypi_name}
Version:        2.2
Release:        %{rel}%{?dist}
Summary:        pyconnectit REST interface base plugins
Source0:        %{pypi_name}-%{version}.tar.gz

License:        MIT

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-arago-pyconnectit-common-base}
%{?scl:Requires: %{scl}-python-arago-pyconnectit-common-rest}
%{?scl:Requires: %{scl}-python-arago-common-base}
%{?scl:Requires: %{scl}-python-falcon}
%{?scl:Requires: %{scl}-python-ujson}

%description
pyconnectit REST interface base plugins

%prep
cp -ax /home/vagrant/compile/ActionHandlers/python-actionhandler /tmp/%{pypi_name}-%{version}
cd /tmp
tar -czf /home/vagrant/rpmbuild/SOURCES/%{pypi_name}-%{version}.tar.gz %{pypi_name}-%{version}
rm -rf %{pypi_name}-%{version}
cd -
%setup -q -n %{pypi_name}-%{version}

%build
%{?scl:scl enable %{scl} "}
%{__python} setup-pyconnectit-common-rest-plugins-base.py build
%{?scl:"}

%install
# Explicitly specify --install-purelib %{python_sitelib}, which is now overriden
# to point to vt191, otherwise Python will try to install into the python27
# Software Collection site-packages directory
%{?scl:scl enable %{scl} "}
%{__python} setup-pyconnectit-common-rest-plugins-base.py install -O1 --skip-build --root %{buildroot} --install-scripts %{python_scriptdir} --install-purelib %{python_sitelib} --install-data %{python_sharedir}
%{?scl:"}

%files
%{python_sitelib}/arago/pyconnectit/common/rest/plugins/*
%{python_sitelib}/arago_pyconnectit_common_rest_plugins_base-*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
