%{?scl:%scl_package sap-rfc-actionhandler}
%{!?scl:%global pkg_name %{name}}

%global pypi_name sap-rfc-actionhandler
%{!?rel:%global rel 1}

Name:           %{?scl_prefix}%{pypi_name}
Version:        0.1.1
Release:        %{rel}%{?dist}
Summary:        ActionHandler for Remote Function Calls in SAP
Source0:        %{pypi_name}-%{version}.tar.gz

License:        MIT

BuildArch:      noarch
BuildRequires:  %{?scl_prefix_python}python-devel
BuildRequires:  %{?scl_prefix_python}python-setuptools
%{?scl:BuildRequires: %{scl}-build %{scl}-runtime}
%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-python-arago-pyactionhandler}
%{?scl:Requires: %{scl}-python-requests}

%description
Executes Remote Function Calls in SAP using its REST interface

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
%{__python} setup.py install -O1 --skip-build --root %{buildroot} --install-scripts %{python_scriptdir} --install-purelib %{python_sitelib} --install-data %{python_sharedir}
%{?scl:"}

%files
%attr(0755, arago, arago) %{python_scriptdir}/hiro-sap-rfc-actionhandler.py
%attr(0755, root, root) /etc/init.d/hiro-sap-rfc-actionhandler
%config(noreplace) /opt/autopilot/conf/external_actionhandlers/sap-rfc-actionhandler*.conf
%config(noreplace) /opt/autopilot/conf/external_actionhandlers/capabilities/sap-rfc-actionhandler.*
%{python_sitelib}/sap_rfc_actionhandler-*

%post
[[ ! -e /var/log/autopilot/engine/sap-rfc-handler.log ]] && touch /var/log/autopilot/engine/sap-rfc-handler.log
[[ -f /var/log/autopilot/engine/sap-rfc-handler.log ]] && chown arago:arago /var/log/autopilot/engine/sap-rfc-handler.log && chmod 644 /var/log/autopilot/engine/sap-rfc-handler.log
chkconfig --add hiro-sap-rfc-actionhandler

