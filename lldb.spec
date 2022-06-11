Name:		lldb
Version:	12.0.1
Release:	2
Summary:	Next generation high-performance debugger

License:	NCSA
URL:		http://lldb.llvm.org/
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{name}-%{version}.src.tar.xz

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-test = %{version}
BuildRequires:	clang-devel = %{version}
BuildRequires:	ncurses-devel
BuildRequires:	swig
BuildRequires:	llvm-static = %{version}
BuildRequires:	libffi-devel
BuildRequires:	zlib-devel
BuildRequires:	libxml2-devel
BuildRequires:	libedit-devel
BuildRequires:	python3-lit
BuildRequires:	multilib-rpm-config

Requires:	python3-lldb

# For origin certification
BuildRequires:	gnupg2

Patch0:     0001-PATCH-lldb-Portable-asm-ptrace.h-include.patch
Patch1:     0002-PATCH-lldb-Support-DWARF-5-DW_FORM_line_strp-used-by.patch
Patch2:     0003-add-EM_RISCV-in-ELFHeader.patch
Patch3:     0004-apply-patch-for-ABISysV.patch
Patch4:     0005-add-new-files-to-CMakeLists.patch
Patch5:     0006-add-some-reg-info-for-RISC-V.patch

%description
%ifarch riscv64
!!NOTE!!: This project has initially added some support for riscv64
and only provide simple functions like the frontend of lldb.
%endif
LLDB is a next generation, high-performance debugger. It is built as a set
of reusable components which highly leverage existing libraries in the
larger LLVM Project, such as the Clang expression parser and LLVM
disassembler.

%package devel
Summary:	Development header files for LLDB
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description devel
The package contains header files for the LLDB debugger.

%package -n python3-lldb
%{?python_provide:%python_provide python3-lldb}
Summary:	Python module for LLDB
BuildRequires:	python3-devel
BuildRequires:	python3-setuptools
Requires:	python3-six
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description -n python3-lldb
The package contains the LLDB Python module.

%prep
%autosetup -n %{name}-%{version}.src -p2

%build

mkdir -p _build
cd _build

# Python version detection is broken
%ifarch riscv64
LDFLAGS="%{__global_ldflags} -latomic -lpthread -ldl"
%else
LDFLAGS="%{__global_ldflags} -lpthread -ldl"
%endif

CFLAGS="%{optflags} -Wno-error=format-security"
CXXFLAGS="%{optflags} -Wno-error=format-security"

%cmake  .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_CONFIG:FILEPATH=/usr/bin/llvm-config-%{__isa_bits} \
	\
	-DLLDB_DISABLE_CURSES:BOOL=OFF \
	-DLLDB_DISABLE_LIBEDIT:BOOL=OFF \
	-DLLDB_DISABLE_PYTHON:BOOL=OFF \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64 \
%else
	-DLLVM_LIBDIR_SUFFIX= \
%endif
	\
	-DPYTHON_EXECUTABLE:STRING=%{__python3} \
	-DPYTHON_VERSION_MAJOR:STRING=$(%{__python3} -c "import sys; print(sys.version_info.major)") \
	-DPYTHON_VERSION_MINOR:STRING=$(%{__python3} -c "import sys; print(sys.version_info.minor)") \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DCLANG_LINK_CLANG_DYLIB=ON \
	-DLLVM_LIT_ARGS="-sv \
	--path %{_libdir}/llvm" \

make %{?_smp_mflags}

%install
cd _build
make install DESTDIR=%{buildroot}

# remove static libraries
rm -fv %{buildroot}%{_libdir}/*.a

# python: fix binary libraries location
liblldb=$(basename $(readlink -e %{buildroot}%{_libdir}/liblldb.so))
ln -vsf "../../../${liblldb}" %{buildroot}%{python3_sitearch}/lldb/_lldb.so
%py_byte_compile %{__python3} %{buildroot}%{python3_sitearch}/lldb

# remove bundled six.py
rm -f %{buildroot}%{python3_sitearch}/six.*

%ldconfig_scriptlets

%check


%files
%license LICENSE.TXT
%{_bindir}/lldb*
%{_libdir}/liblldb.so.*
%{_libdir}/liblldbIntelFeatures.so.*

%files devel
%{_includedir}/lldb
%{_libdir}/*.so

%files -n python3-lldb
%{python3_sitearch}/lldb

%changelog
* Wed Jun 08 2022 yangjinghua <yjhdandan@163.com> - 12.0.1-2
- initial riscv64 support

* Thu Jan 06 2022 Chen Chen <chen_aka_jan@163.com> - 12.0.1-1
- upgrade lldb to 12.0.1

* Mon Oct 12 2020 wangxiao <wangxiao65@huawei.com> - 10.0.1-1
- upgrade lldb to 10.0.1

* Mon Dec 2 2019 likexin <likexin@huawei.com> 7.0.0-2
- Package init
