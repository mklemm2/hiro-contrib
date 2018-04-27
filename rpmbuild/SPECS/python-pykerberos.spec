%{?scl:%scl_package python-pykerberos}
%{!?scl:%global pkg_name %{name}}

%global pypi_name pykerberos

Name:           %{?scl_prefix}python-pykerberos
Version:        1.2.1
Release:        beta1%{?dist}
Summary:        High-level interface to Kerberos

License:        Apache
URL:            https://github.com/02strich/pykerberos
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      x86_64
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  libevent-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
BuildRequires:  gcc
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime krb5-devel}
%{?scl:Requires: %{scl}-runtime krb5-libs}

%description
This Python package is a high-level wrapper for
Kerberos (GSSAPI) operations. The goal is to avoid
having to build a module that wraps the entire
Kerberos.framework, and instead offer a limited set
of functions that do what is needed for
client/server Kerberos authentication based on
<http://www.ietf.org/rfc/rfc4559.txt>.

%prep
cp -ax /home/vagrant/compile/pykerberos /tmp/%{pypi_name}-%{version}
cd /tmp
tar -czf /home/vagrant/rpmbuild/SOURCES/%{pypi_name}-%{version}.tar.gz %{pypi_name}-%{version}
rm -rf %{pypi_name}-%{version}
cd -
%setup -q -n %{pypi_name}-%{version}
%global _python_bytecompile_errors_terminate_build 0

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
%{python_sitelib}/kerberos*.so
#%{python_includedir}/%{pypi_name}*

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
