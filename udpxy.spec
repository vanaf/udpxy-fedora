%global realversion 1.0-Chipmunk-19

Name:           udpxy
Version:        1.0.19
Release:        2%{?dist}
Summary:        UDP-to-HTTP multicast traffic relay daemon

Group:          Applications/Internet
License:        GPLv3+
URL:            http://sourceforge.net/projects/udpxy/
Source0:        http://downloads.sourceforge.net/%{name}/%{name}.%{realversion}.tgz
Source1:        %{name}.service
Source2:        %{name}.init
Source3:        %{name}.sysconfig


BuildRequires:  systemd-units

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description
udpxy is a UDP-to-HTTP multicast traffic relay daemon:
it forwards UDP traffic from a given multicast subscription
to the requesting HTTP client.

%prep
%setup -q -n %{name}-%{realversion}

chmod a-x CHANGES
sed -i "s|CFLAGS += -W -Wall -Werror --pedantic|CFLAGS += %{optflags}|g" Makefile

%build
make %{?_smp_mflags}


%install
rm -rf %{buildroot}

sed -i "s|INSTALLROOT := /usr/local|INSTALLROOT := %{buildroot}/usr|g" Makefile
sed -i 's|ln -s $(INSTALLROOT)/bin/$(EXEC)|ln -s $(EXEC)|g' Makefile

make install

install -D -p -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

install -D -p -m755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}
install -D -p -m644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{name}


%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    /sbin/chkconfig --add udpxy

fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable udpxy.service > /dev/null 2>&1 || :
    /bin/systemctl stop udpxy.service > /dev/null 2>&1 || :
    /sbin/service udpxy stop &> /dev/null
    /sbin/chkconfig --del udpxy

fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart udpxy.service >/dev/null 2>&1 || :
fi


%files
%defattr(-,root,root,-)
%doc README CHANGES gpl.txt
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_initrddir}/%{name}
%{_bindir}/%{name}
%{_bindir}/udpxrec
%{_unitdir}/%{name}.service


%changelog
* Sun May 22 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 1.0.19-2
- init script reverted for compatibility
- options moved to sysconfdir
- systemd type now 'forking'


* Sun May 22 2011 Alexey Kurov <nucleo@fedoraproject.org> - 1.0.19-1
- udpxy 1.0-Chipmunk-19
- service disabled by default
- SysV init script replaced with systemd unit
- options from sysconfdir moved to unit file

* Sun Aug  1 2010 Alexey Kurov <nucleo@fedoraproject.org> - 1.0.16-1
- Initial RPM release
