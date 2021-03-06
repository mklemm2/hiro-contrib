# rpmrebuild autogenerated specfile

%define defaultbuildroot /
AutoProv: no
%undefine __find_provides
AutoReq: no
%undefine __find_requires
# Do not try autogenerate prereq/conflicts/obsoletes and check files
%undefine __check_files
%undefine __find_prereq
%undefine __find_conflicts
%undefine __find_obsoletes
# Be sure buildpolicy set to do nothing
%define __spec_install_post %{nil}
# Something that need for rpm-4.1
%define _missing_doc_files_terminate_build 0
#dummy
#dummy
#BUILDHOST:    c1bg.rdu2.centos.org
#BUILDTIME:    Fri Oct  2 09:46:21 2015

#RPMVERSION:   4.8.0

#INSTALLTIME:  Tue Feb 14 10:35:02 2017

#OS:           linux
#SIZE:           88697
#ARCHIVESIZE:           91376
#ARCH:         noarch
BuildArch:     noarch
Name:          rh-python34-python-setuptools
Version:       38.2.4
Release:       1.el6
License:       MIT 
Group:         Development/Languages
Summary:       Python 2 and 3 compatibility utilities
Distribution:  Centos

URL:           https://github.com/pypa/setuptools
Source0:       https://files.pythonhosted.org/packages/source/s/setuptools/setuptools-38.2.4.zip
Vendor:        Centos
Packager:      CBS <cbs@centos.org>
Provides:      rh-python34-python-setuptools = 38.2.4-1.el6
Requires:      rh-python34-python(abi) = 3.4
#Requires:      rpmlib(CompressedFileNames) <= 3.0.4-1
#Requires:      rpmlib(FileDigests) <= 4.6.0-1
#Requires:      rpmlib(PartialHardlinkSets) <= 4.0.4-1
#Requires:      rpmlib(PayloadFilesHavePrefix) <= 4.0-1
#Requires:      rpmlib(PayloadIsXz) <= 5.2-1
#suggest
#enhance
%description
Easily download, build, install, upgrade, and uninstall Python packages

%prep
%setup -q -n setuptools-38.2.4

%build
%{?scl_python:scl enable %{scl_python} "}
%{__python} setup.py build
%{?scl_python:"}

%install
# Explicitly specify --install-purelib %{python_sitelib}, which is now overriden
# to point to vt191, otherwise Python will try to install into the python27
# Software Collection site-packages directory
%{?scl_python:scl enable %{scl_python} "}
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-purelib %{python34python3_sitelib}
%{?scl_python:"}

#This is the Python 3 build of the module.
%files
%{python34python3_sitelib}/setuptools*

