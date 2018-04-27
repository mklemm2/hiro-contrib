# define name of the scl
%global scl hiro_integration
%scl_package %scl

# Defaults for the values for the python34/rh-python35 Software Collection. These
# will be used when python34-scldevel (or rh-python35-scldevel) is not in the
# build root
%{!?scl_python:%global scl_python python34}
%{!?scl_prefix_python:%global scl_prefix_python %{scl_python}-}

# Only for this build, you need to override default __os_install_post,
# because the default one would find /opt/.../lib/python2.7/ and try
# to bytecompile with the system /usr/bin/python2.7
%global __os_install_post %{python34_os_install_post}
# Similarly, override __python_requires for automatic dependency generator
%global __python_requires %{python34_python_requires}

# The directory for site packages for this Software Collection
%global hiro_integration_sitelib %(echo %{python34python_sitelib} | sed 's|%{scl_python}|%{scl}|')

Summary: Package that installs %scl
Name: %scl_name
Version: 1.2
Release: 1%{?dist}
License: MIT
BuildRequires: scl-utils-build
# Always make sure that there is the python37-sclbuild (or rh-python35-sclbuild)
# package in the build root
BuildRequires: %{scl_prefix_python}scldevel
# Require python34-python-devel, you will need macros from that package
BuildRequires: %{scl_prefix_python}python-devel
Requires: %{scl_prefix}python-versiontools

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils
Requires: %{scl_prefix_python}runtime

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build
# Require python34-scldevel (or rh-python35-scldevel) so that there is always access
# to the %%scl_python and %%scl_prefix_python macros in builds for this Software
# Collection
Requires: %{scl_prefix_python}scldevel

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%prep
%setup -c -T

%install
%scl_install

# Create the enable scriptlet that:
# - Adds an additional load path for the Python interpreter.
# - Runs scl_source so that you can run:
#     scl enable hiro_integration "bash"
#   instead of:
#     scl enable python34 hiro_integration "bash"

cat >> %{buildroot}%{_scl_scripts}/enable << EOF
. scl_source enable %{scl_python}
export PYTHONPATH="%{hiro_integration_sitelib}\${PYTHONPATH:+:\${PYTHONPATH}}"
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export PYTHON_DATADIR=/opt/rh/%{scl}/root/usr/share

EOF

mkdir -p %{buildroot}%{hiro_integration_sitelib}

# - Enable Software Collection-specific bytecompilation macros from
#   the python34-python-devel package.
# - Also override the %%python_sitelib macro to point to the hiro_integration Software
#   Collection.
# - If you have architecture-dependent packages, you will also need to override
#   the %%python_sitearch macro.

cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config << EOF
%%scl_package_override() %%{expand:%{?python34_os_install_post:%%global __os_install_post %%python34_os_install_post}
%%global __python_requires %%python34_python_requires
%%global __python_provides %%python34_python_provides
%%global __python %python34__python
%%global python_sitelib %hiro_integration_sitelib
%%global python2_sitelib %hiro_integration_sitelib
%%global python_includedir /opt/rh/%{scl}/root/usr/include/python3.4m
%%global python_scriptdir /opt/rh/%{scl}/root/usr/bin
%%global python_sharedir /opt/rh/%{scl}/root/usr/share
}
EOF

%files

%files runtime -f filelist
%scl_files
%hiro_integration_sitelib

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%changelog
* Wed Jan 22 2014 John Doe <jdoe@example.com> - 1-1
- Initial package.
