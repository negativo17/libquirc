#global tag %{version}

%global commit0 927d680904dc95fdff4cd9d022eb374b438ff8f2
%global date 20250520
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

%global upstream quirc

# SDL 1.2 and SDL_gfx are not in RHEL:
%bcond tools %{?rhel:0}%{!?rhel:1}

# Version of the library as set by the upstream Makefile, and the SONAME the
# library is built with. Upstream links the library without a SONAME at all, so
# it is passed in below.
%global libver 1.2
%global sover 1

Name:           libquirc
Version:        1.2%{!?tag:^%{date}git%{shortcommit0}}
Release:        1%{?dist}
Summary:        QR decoder library
License:        ISC
URL:            https://github.com/dlbeer/quirc

%if 0%{?tag:1}
Source0:        %{url}/archive/v%{version}/%{upstream}-%{version}.tar.gz
%else
Source0:        %{url}/archive/%{commit0}.tar.gz#/%{upstream}-%{shortcommit0}.tar.gz
%endif

BuildRequires:  gcc
BuildRequires:  make
%if %{with tools}
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  pkgconfig(sdl)
BuildRequires:  SDL_gfx-devel
%endif

%description
quirc is a library for extracting and decoding QR codes from images. It is
able to find and decode the codes in an image without any user intervention,
and is small enough to be used on embedded systems.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%if %{with tools}
%package        tools
Summary:        QR code scanning demos for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    tools
Demo programs built on %{name}: quirc-demo scans QR codes from a V4L2 camera
and quirc-inspect shows what the decoder does with a still image.
%endif

%prep
%if 0%{?tag:1}
%autosetup -p1 -n %{upstream}-%{version}
%else
%autosetup -p1 -n %{upstream}-%{commit0}
%endif

%build
# The Makefile picks up the SDL flags with "pkg-config --cflags sdl 2>&1", which
# puts the error message in the compiler flags instead of failing.
sdl_cflags=
%if %{with tools}
sdl_cflags=$(pkg-config --cflags sdl)
%endif

# Upstream links the library without a SONAME, add it through the link flags.
%make_build libquirc.so \
    SDL_CFLAGS="${sdl_cflags}" \
    CFLAGS="%{build_cflags} -fPIC" \
    LDFLAGS="%{build_ldflags} -Wl,-soname,%{name}.so.%{sover}"

%if %{with tools}
# Linked separately, otherwise the demos get the SONAME too.
%make_build sdl \
    SDL_CFLAGS="${sdl_cflags}" \
    CFLAGS="%{build_cflags} -fPIC" \
    LDFLAGS="%{build_ldflags}"
%endif

%install
# "make install" is not usable: it installs as root:root, into %%{_prefix}/lib
# rather than %%{_libdir}, and wants the V4L demo too.
install -p -m 0755 -D %{name}.so.%{libver} %{buildroot}%{_libdir}/%{name}.so.%{libver}
ln -s %{name}.so.%{libver} %{buildroot}%{_libdir}/%{name}.so.%{sover}
ln -s %{name}.so.%{sover} %{buildroot}%{_libdir}/%{name}.so

install -p -m 0644 -D lib/%{upstream}.h %{buildroot}%{_includedir}/%{upstream}.h

%if %{with tools}
# Upstream does not install "inspect" at all, and the name is too generic here.
install -p -m 0755 -D quirc-demo %{buildroot}%{_bindir}/quirc-demo
install -p -m 0755 -D inspect %{buildroot}%{_bindir}/quirc-inspect
%endif

%files
%license LICENSE
%doc README.md
%{_libdir}/%{name}.so.%{libver}
%{_libdir}/%{name}.so.%{sover}

%files devel
%{_includedir}/%{upstream}.h
%{_libdir}/%{name}.so

%if %{with tools}
%files tools
%{_bindir}/quirc-demo
%{_bindir}/quirc-inspect
%endif

%changelog
* Fri Sep 18 2026 Simone Caronni <negativo17@gmail.com> - 1.2^20250520git927d680-1
- First build.
