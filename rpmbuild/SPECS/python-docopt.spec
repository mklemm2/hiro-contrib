%{?scl:%scl_package python-docopt}
%{!?scl:%global pkg_name %{name}}

%global pypi_name docopt

Name:           %{?scl_prefix}python-docopt
Version:        0.6.2
Release:        1%{?dist}
Summary:        Smart replacement for plain tuple used in __version__

License:        LGPLv3
URL:            https://docopt.org
Source0:        https://pypi.python.org/packages/a2/55/8f8cab2afd404cf578136ef2cc5dfb50baa1761b68c9da1fb1e4eed343c9/docopt-0.6.2.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
Pythonic argument parser, that will make you smile

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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python_sitelib}
%{?scl:"}

%files
%{python_sitelib}/%{pypi_name}*
%{python_sitelib}/__pycache__/

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1.9.1-1
- Built for vt191 SCL.
