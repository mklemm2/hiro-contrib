%{?scl:%scl_package python-ordereddict}
%{!?scl:%global pkg_name %{name}}

%global pypi_name ordereddict

Name:           %{?scl_prefix}python-ordereddict
Version:        1.1
Release:        1%{?dist}
Summary:        None

License:        MIT
URL:            None
Source0:        https://files.pythonhosted.org/packages/source/o/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}

%description
Drop-in substitute for Py2.7's new collections.OrderedDict. The recipe has big-
oh performance that matches regular dictionaries (amortized O(1)
insertion/deletion/lookup and O(n) iteration/repr/copy/equality_testing).
Originally based on http://code.activestate.com/recipes/576693/

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
