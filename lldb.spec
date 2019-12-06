Name:           lldb
Version:        7.0.0
Release:        2
Summary:        Next-generation high-performance debugger
License:        NCSA
URL:            http://lldb.llvm.org/
Source0:        http://%{?rc_ver:pre}releases.llvm.org/%{version}/%{?rc_ver:rc%{rc_ver}}/%{name}-%{version}%{?rc_ver:rc%{rc_ver}}.src.tar.xz
BuildRequires:  cmake llvm-devel = %{version} clang-devel = %{version} ncurses-devel swig
BuildRequires:  llvm-static = %{version} libffi-devel zlib-devel libxml2-devel libedit-devel
Requires:       python2-lldb

%description
The LLDB Debugger (LLDB) is the debugger component of the LLVM project. It
is built as a set of reusable components which extensively use existing
libraries from LLVM, such as the Clang expression parser and LLVM disassembler.
LLDB is free and open-source software under the University of Illinois/NCSA
Open Source License,[2] a BSD-style permissive software license.

%package devel
Summary:        Development header files for LLDB
Requires:       %{name} = %{version}-%{release}

%description devel
The package contains header files for the LLDB debugger.

%package -n python2-lldb
%{?python_provide:%python_provide python2-lldb}
Summary:        Python module for LLDB
BuildRequires:  python2-devel
Requires:       python2-six

%description -n python2-lldb
The package contains the LLDB Python module.

%prep
%autosetup -n %{name}-%{version}%{?rc_ver:rc%{rc_ver}}.src -p1
sed -i -e "s~import sys~import sys\nsys.path.insert\(1, '%{python2_sitearch}/lldb'\)~g" source/Interpreter/embedded_interpreter.py

%build
mkdir -p _build;cd _build
LDFLAGS="%{__global_ldflags} -lpthread -ldl"
CFLAGS="%{optflags} -Wno-error=format-security"
CXXFLAGS="%{optflags} -Wno-error=format-security"
%cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo -DLLVM_LINK_LLVM_DYLIB:BOOL=ON -DLLVM_CONFIG:FILEPATH=/usr/bin/llvm-config-%{__isa_bits} \
        -DLLDB_PATH_TO_LLVM_BUILD=%{_prefix} -DLLDB_PATH_TO_CLANG_BUILD=%{_prefix} -DLLDB_DISABLE_CURSES:BOOL=OFF \
        -DLLDB_DISABLE_LIBEDIT:BOOL=OFF -DLLDB_DISABLE_PYTHON:BOOL=OFF -DLLVM_LIBDIR_SUFFIX=64 \
        -DPYTHON_EXECUTABLE:STRING=%{__python2} -DPYTHON_VERSION_MAJOR:STRING=$(%{__python2} -c "import sys; print sys.version_info.major") \
        -DPYTHON_VERSION_MINOR:STRING=$(%{__python2} -c "import sys; print sys.version_info.minor")
%make_build

%install
cd _build
%make_install
liblldb=$(basename $(readlink -e %{buildroot}%{_libdir}/liblldb.so))
ln -vsf "../../../${liblldb}" %{buildroot}%{python2_sitearch}/lldb/_lldb.so
mv -v %{buildroot}%{python2_sitearch}/readline.so %{buildroot}%{python2_sitearch}/lldb/readline.so

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%files
%{_bindir}/lldb*
%{_libdir}/liblldb*.so.*

%files devel
%{_includedir}/lldb
%{_libdir}/*.so
%exclude %{_libdir}/*.a
%exclude %{python2_sitearch}/six.*

%files -n python2-lldb
%{python2_sitearch}/lldb

%changelog
* Mon Dec 2 2019 likexin <likexin4@huawei.com> 7.0.0-2
- Package init
