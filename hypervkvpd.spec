# HyperV KVP daemon name
%global hv_kvp_daemon hv_kvp_daemon

Name:     hypervkvpd
Version:  0
Release:  0.9%{?dist}
Summary:  HyperV key value pair (KVP) daemon

Group:    System Environment/Daemons
License:  GPLv2
URL:      http://www.kernel.org
# Source file obtained from kernel upstream.
# git://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git
# The daemon and scripts are located in "master branch - /tools/hv"
Source0:  %{hv_kvp_daemon}.c
Source1:  hv_get_dhcp_info.sh
Source2:  hv_get_dns_info.sh
Source3:  hv_set_ifconfig.sh
Source4:  hypervkvpd

# Correct paths to external scripts ("/usr/libexec/hypervkvpd").
Patch0:   hypervkvpd-0-corrected_paths_to_external_scripts.patch
# rhbz#872593
Patch1:   hypervkvpd-0-Netlink-source-address-validation-allows-DoS.patch
# rhbz#872566
Patch2:   hypervkvpd-0-long_file_names_from_readdir.patch
# rhbz#872584
Patch3:   hypervkvpd-0-var_subdirectory.patch
Patch4:   hypervkvpd-0-string_types.patch
Patch5:   hypervkvpd-0-permissions_of_created_directory_and_files.patch
# rhbz#890301
Patch6:   hypervkvpd-0-fix_a_typo_in_hv_set_ifconfig_sh.patch
Patch7:   hypervkvpd-0-Fix-how-ifcfg-file-is-created.patch
Patch8:   hypervkvpd-0-Use-CLOEXEC-when-opening-kvp_pool-files.patch

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
# this package is supposed to run on RHEL when it's a guest under Hyper-V
ExclusiveArch:    x86_64 i686
BuildRequires:    kernel-devel >= 2.6.32-336
Requires(post):   chkconfig
Requires(preun):  chkconfig
# This is for /sbin/service
Requires(preun):  initscripts
Requires(postun): initscripts

%description
Hypervkvpd is an implementation of HyperV key value pair (KVP) 
functionality for Linux.


%prep
%setup -Tc
cp -pvL %{SOURCE0} %{hv_kvp_daemon}.c
cp -pvL %{SOURCE1} hv_get_dhcp_info.sh
cp -pvL %{SOURCE2} hv_get_dns_info.sh
cp -pvL %{SOURCE3} hv_set_ifconfig.sh
cp -pvL %{SOURCE4} hypervkvpd

%patch0 -p1 -b .external_scripts
%patch1 -p1 -b .netlink_DoS
%patch2 -p1 -b .long_names
%patch3 -p1 -b .var_subdir
%patch4 -p1 -b .string_types
%patch5 -p1 -b .permissions
%patch6 -p1
%patch7 -p3 -b .ifcfg_fix
%patch8 -p3 -b .use_CLOEXEC


%build
# kernel-devel version
%{!?kversion: %global kversion `ls %{_usrsrc}/kernels | sort -dr | head -n 1`}

gcc \
    %{optflags} \
    -I%{_usrsrc}/kernels/%{kversion}/include \
    %{hv_kvp_daemon}.c \
    -o %{hv_kvp_daemon}


%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_sbindir}
install -p -m 0755 %{hv_kvp_daemon} %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_initrddir}
# SysV init script
install -p -m 0755 %{SOURCE4} %{buildroot}%{_initrddir}
# Shell scripts for the daemon
mkdir -p %{buildroot}%{_libexecdir}/%{name}
install -p -m 0755 hv_get_dhcp_info.sh %{buildroot}%{_libexecdir}/%{name}/hv_get_dhcp_info
install -p -m 0755 hv_get_dns_info.sh %{buildroot}%{_libexecdir}/%{name}/hv_get_dns_info
install -p -m 0755 hv_set_ifconfig.sh %{buildroot}%{_libexecdir}/%{name}/hv_set_ifconfig
# Directory for pool files
mkdir -p %{buildroot}%{_sharedstatedir}/hyperv


%post
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add hypervkvpd


%preun
# Removing package
if [ $1 -eq 0 ] ; then
    /sbin/service hypervkvpd stop >/dev/null 2>&1
    /sbin/chkconfig --del hypervkvpd
fi


%postun
# Updating package
if [ "$1" -ge "1" ] ; then
    /sbin/service hypervkvpd condrestart >/dev/null 2>&1 || :
fi
# If removing the package, delete %%{_sharedstatedir}/hyperv directory
if [ "$1" -eq "0" ] ; then
    rm -rf %{_sharedstatedir}/hyperv || :
fi


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc
%{_sbindir}/%{hv_kvp_daemon}
%{_initrddir}/hypervkvpd
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/hv_get_dhcp_info
%{_libexecdir}/%{name}/hv_get_dns_info
%{_libexecdir}/%{name}/hv_set_ifconfig
%dir %{_sharedstatedir}/hyperv


%changelog
* Mon Jan 14 2013 Tomas Hozza <thozza@redhat.com> - 0-0.9
- Fix a typo in hv_set_ifconfig.sh script
- Fix creation process of ifcfg-* files when doing IP injection
- Use CLOEXEC when opening pool files to prevent FD leaking
- Changes in SPEC file:
 - remove/create %%{_sharedstatedir}/hyperv if removing/installing package
 - install scripts without ".sh" extension

* Mon Nov 12 2012 Tomas Hozza <thozza@redhat.com> - 0-0.8
- Bumping release to 0.8 to avoid update path from RHEL5
- changing the way how Netlink source address is validated (#872593)
- fix for long names from readdir (#872566)
- applied reasonable Debian/Ubuntu patches (#872584)

* Thu Nov 08 2012 Tomas Hozza <thozza@redhat.com> - 0-0.2
- Changing ExclusiveArch just to x86_64 i686 (#870288)

* Tue Sep 25 2012 Tomas Hozza <thozza@redhat.com> - 0-0.1
- Initial spec file
