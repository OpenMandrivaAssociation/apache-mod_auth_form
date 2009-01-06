#Module-Specific definitions
%define mod_name mod_auth_form
%define mod_conf A84_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Form-based, authorization module using MySQL and session management
Name:		apache-%{mod_name}
Version:	2.05
Release:	%mkrel 8
Group:		System/Servers
License:	Apache License
URL:		http://www.csce.uark.edu/~ajarthu/mod_auth_form/
Source0:	%{mod_name}-%{version}-src.tar.gz
Source1:	%{mod_conf}
Source2:	README.html
Source3:	index.css
Patch0:		mod_auth_form-avoid-version.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	mysql-devel
BuildRequires:  file
BuildRequires:  autoconf2.5
BuildRequires:  automake1.7
BuildRequires:  libtool
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This module is a form-based authorization module based on 'mod_auth_mysql' and
'mod_auth_sim'. It is used to place access restrictions on a per-directory, 
per-user-request basis using session management. The module uses a MySQL
database to retrieve users' group membership, maintain and validate users'
sessions, and optionally track user activity.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0

cp %{SOURCE2} README.html
cp %{SOURCE3} index.css
cp %{SOURCE1} %{mod_conf}

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done
    
# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
rm -rf configure autom4te.cache
libtoolize --copy --force; aclocal-1.7; autoconf; automake-1.7 --add-missing --copy --foreign; autoconf

export APXS="%{_sbindir}/apxs"
export APACHE2_INCLUDE="`$APXS -q INCLUDEDIR`"
export CPPFLAGS="`%{_bindir}/apr-1-config --cppflags`"

%configure2_5x --localstatedir=/var/lib

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -m0755 src/.libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
 %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
 if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
 fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README* index.css AUTHORS COPYING ChangeLog INSTALL NEWS
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}


