#  @file make_qml_dbus_cpp.py
#  @brief Generator of QML to QDbus C++ part
#
# This file is a part of HMI D-Bus layer.
# 
# Copyright (c) 2013, Ford Motor Company
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the
# distribution.
#
# Neither the name of the Ford Motor Company nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 'A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from argparse import ArgumentParser
import os.path
from xml.etree import ElementTree
from copy import copy
from ford_xml_parser import FordXmlParser

class Impl(FordXmlParser):
    def make_dbus_type_declarations(self, out):
        for struct in self.structs.items():
            self.write_struct_declaration(struct, out)


    def make_dbus_metatype_declarations(self, out):
        for struct in self.structs.items():
            self.write_struct_metatype_declaration(struct, out)


    def write_struct_declaration(self, ((iface, name), params), out):
        struct_name = iface + '_' + name
        out.write("struct " + struct_name + " {\n")
        for param in params:
            out.write("  " + self.qt_param_type(param) + " " + param.name + ";\n")
        out.write("};\n")
        out.write('QDBusArgument& operator << (QDBusArgument&, const ' + struct_name + "&);\n")
        out.write('const QDBusArgument& operator >> (const QDBusArgument&, ' + struct_name + "&);\n")
        out.write('void PutArgToMap(QVariantMap& map, const char* name, const ' + struct_name + "& v);\n")
        out.write('QVariant ValueToVariant(' + struct_name + "& v);\n")
        out.write('QVariant ValueToVariant(QList<' + struct_name + " >& v);\n")
        out.write('bool GetArgFromMap(const QVariantMap& map, const char* name, ' + struct_name + "& v);\n")
        out.write('bool VariantToValue(const QVariant& variant, ' + struct_name + "& v);\n")
        out.write('bool VariantToValue(const QVariant& variant, QList<' + struct_name + " >& v);\n")


    def write_struct_metatype_declaration(self, ((iface, name), params), out):        
        struct_name = iface + '_' + name
        out.write('Q_DECLARE_METATYPE(' + struct_name + ")\n")
        out.write('Q_DECLARE_METATYPE(OptionalArgument<' + struct_name + ">)\n")
        out.write('Q_DECLARE_METATYPE(QList<' + struct_name + ">)\n")
        out.write('Q_DECLARE_METATYPE(OptionalArgument<QList<' + struct_name + "> >)\n\n")
            

    def make_dbus_type_definitions(self, out):
        for struct in self.structs.items():
            self.write_struct_definition(struct, out)


    def write_struct_definition(self, ((iface, name), params), out):
        struct_name = iface + '_' + name
        out.write('QDBusArgument& operator << (QDBusArgument& arg, const ' + struct_name + "& v) {\n")
        out.write("  arg.beginStructure();\n")
        for param in params:
            out.write("  arg << v." + param.name + ";\n")
        out.write("  arg.endStructure();\n")
        out.write("  return arg;\n")
        out.write("}\n")

        out.write('const QDBusArgument& operator >> (const QDBusArgument& arg, ' + struct_name + "& v) {\n")
        out.write("  arg.beginStructure();\n")
        for param in params:
            out.write("  arg >> v." + param.name + ";\n")
        out.write("  arg.endStructure();\n")
        out.write("  return arg;\n")
        out.write("}\n")
        out.write('QVariant ValueToVariant(const ' + struct_name + "& v) {\n")
        out.write("  QVariantMap map;\n")
        for param in params:
            out.write("  PutArgToMap(map, \"" + param.name + "\", v." + param.name + ");\n")
        out.write("  return QVariant::fromValue(map);\n")
        out.write("}\n")
        out.write('QVariant ValueToVariant(const QList<' + struct_name + ">& v) {\n")
        out.write("  QList<QVariant> ret;\n")
        out.write("  for (QList<" + struct_name + ">::const_iterator i = v.begin(); i != v.end(); ++i) ret.append(ValueToVariant(*i));\n");
        out.write("  return QVariant::fromValue(ret);\n");
        out.write("}\n")
        out.write('void PutArgToMap(QVariantMap& map, const char* name, const ' + struct_name + "& v) {\n")
        out.write("  map.insert(name, ValueToVariant(v));\n")
        out.write("}\n")
        out.write('bool VariantToValue(const QVariant& variant, ' + struct_name + "& v) {\n")
        out.write("  if (variant.type() != QVariant::Map) return false;\n")
        out.write("  QVariantMap map = variant.toMap();\n")
        for param in params:
            out.write("  if (!GetArgFromMap(map, \"" + param.name + "\", v." + param.name + ")) return false;\n")
        out.write("  return true;\n")
        out.write("}\n")
        out.write('bool VariantToValue(const QVariant& variant, QList<' + struct_name + ">& v) {\n")
        out.write("  if (variant.type() != QVariant::List) return false;\n")
        out.write("  QList<QVariant> list = variant.toList();\n")
        out.write("  for (QList<QVariant>::const_iterator i = list.begin(); i != list.end(); ++i) {\n");
        out.write("    " + struct_name + " s;\n");
        out.write("    if (!VariantToValue(*i, s)) return false;\n");
        out.write("    v.append(s);\n");
        out.write("  }\n")
        out.write("  return true;\n")
        out.write("}\n")
        out.write('bool GetArgFromMap(const QVariantMap& map, const char* name, ' + struct_name + "& v) {\n")
        out.write("  QVariantMap::const_iterator it = map.find(name);\n")
        out.write("  if (map.end() == it) return false;\n")
        out.write("  if (it->type() != QVariant::Map) return false;\n")
        out.write("  const QVariantMap& inmap = it->toMap();\n")
        for param in params:
            out.write("  if (!GetArgFromMap(inmap, \"" + param.name + "\", v." + param.name + ")) return false;\n")
        out.write("  return true;\n")
        out.write("}\n")
        out.write("\n")
            

    def qt_param_type(self, param):
        if not param.mandatory:
            param_copy = copy(param)
            param_copy.mandatory = True
            return "OptionalArgument<" + self.qt_param_type(param_copy) + "> "
        if param.array:
            param_copy = copy(param)
            param_copy.array = False
            return "QList<" + self.qt_param_type(param_copy) + "> "
        if param.type == 'Integer' or param.enum:
            return 'int'
        elif param.type == 'String':
            return 'QString'
        elif param.type == 'Boolean':
            return 'bool'
        elif param.type == 'Float':
            return 'double'
        elif param.struct:
            return param.fulltype[0] + '_' + param.fulltype[1]
        return 'xxx'


    def from_variant_func_name(self, param, interface):
        prefix = ''
        if not param.mandatory:
            param_copy = copy(param)
            param_copy.mandatory = True
            return 'opt_' + self.from_variant_func_name(param_copy, interface)
        if param.array:
            param_copy = copy(param)
            param_copy.array = False
            return 'arr_' + self.from_variant_func_name(param_copy, interface)

        if param.type in ['Integer', 'String', 'Boolean', 'Float']:
            param_type = param.type
        else:
            param_type = param.type.split('.')
            if len(param_type) > 1:
                param_type = (param_type[0], param_type[1])
            else:
                param_type = (interface, param_type[0])
            if param_type in self.structs:
                param_type = param_type[0] + '_' + param_type[1]
            elif param_type in self.enums:
                param_type = 'Integer'
        return param_type + '_from_variant'


    def make_method_signature(self, request, response, interface, add_classname):
        in_params = request.findall('param')
        out_params = response.findall('param')
        if out_params:
            ret_param_desc = self.make_param_desc(out_params[0], interface)
            ret_type = self.qt_param_type(ret_param_desc)
        else:
            ret_type = 'void'
        retstr = ret_type + ' '
        if add_classname:
            retstr = retstr + interface + 'Adaptor::'
        retstr = retstr + request.get('name') + '('
        in_params_num = len(in_params)
        for i in range(0, in_params_num):
            param_desc = self.make_param_desc(in_params[i], interface)
            param_type = self.qt_param_type(param_desc)
            retstr = retstr + param_type + ' ' + param_desc.name + '_in'
            if i <> in_params_num - 1: retstr = retstr + ", "
        out_params_num = len(out_params)
        if out_params_num > 1:
            if in_params_num > 0:
                retstr = retstr + ", "
            for i in range(1, out_params_num):
                param_desc = self.make_param_desc(out_params[i], interface)
                param_type = self.qt_param_type(param_desc)
                retstr = retstr + param_type + '& ' + param_desc.name + '_out'
                if i <> out_params_num - 1: retstr = retstr + ", "
        retstr = retstr + ')'
        return retstr


    def make_signal_signature(self, signal, interface, add_void):
        params = signal.findall('param')
        if add_void:
            retstr = 'void '
        else:
            retstr = ''
        retstr = retstr + signal.get('name') + '('
        params_num = len(params)
        for i in range(0, params_num):
            param_desc = self.make_param_desc(params[i], interface)
            param_type = self.qt_param_type(param_desc)
            retstr = retstr + param_type + ' ' + param_desc.name
            if i <> params_num - 1: retstr = retstr + ", "
        retstr = retstr + ')'
        return retstr


    def make_qml_signal_signature(self, signal, interface, name, short=False, add_classname=False):
        params = signal.findall('param')
        if short:
            retstr = ''
        else:
            retstr = 'void '
        if add_classname:
            retstr = retstr + interface + 'Adaptor::'
        retstr = retstr + name + '('
        params_num = len(params)
        for i in range(0, params_num):
            param_desc = self.make_param_desc(params[i], interface)
            if param_desc.struct or param_desc.array or not param_desc.mandatory: typ = 'QVariant'
            elif param_desc.type == 'Integer' or param_desc.enum: typ = 'int'
            elif param_desc.type == 'Boolean': typ = 'bool'
            elif param_desc.type == 'Float': typ = 'double'
            elif param_desc.type == 'String': typ = 'QString'
            else: typ = 'QVariant'
            retstr = retstr + typ
            if not short: retstr = retstr + ' ' + param_desc.name
            if i <> params_num - 1: retstr = retstr + ", "
        retstr = retstr + ')'
        return retstr


    def write_adaptor_declaration(self, interface_el, notifications, request_responses, out):
        def glue_strings(strings):
            ret = list()
            curstr = ''
            for str in strings:
                curstr = curstr + str
                if(str[-1] == '>'):
                    ret.append(curstr)
                    curstr = ''
            return ret
        ifacename = interface_el.get('name')
        out.write("class " + ifacename + "Adaptor : public QDBusAbstractAdaptor {\n");
        out.write("  Q_OBJECT\n");
        out.write("  Q_CLASSINFO(\"D-Bus Interface\", \"" + self.interface_path + '.' + ifacename + "\")\n");
        out.write("  Q_CLASSINFO(\"D-Bus Introspection\",\n");
        introspection_el = self.create_introspection_iface_el(interface_el)
        introspection = glue_strings(ElementTree.tostringlist(introspection_el))
        for str in introspection: 
            str = str.replace('"', '\\"')
            out.write('"' + str + '"' + "\n")
        out.write("  )\n")
        out.write(" public:\n")
        out.write("  explicit " + ifacename + "Adaptor(QObject *parent = 0);\n")
        out.write("  void SetApi(QQuickItem*);\n")
        out.write(" public slots:\n")
        for (request, response) in request_responses:
            signature = self.make_method_signature(request, response, ifacename, False)
            out.write("  " + signature + ";\n")
        out.write(" signals:\n")
        for n in notifications:
            signature = self.make_signal_signature(n, ifacename, True)
            out.write("  " + signature + ";\n")
        out.write(" private slots:\n")
        for n in notifications:
            signature = self.make_qml_signal_signature(n, ifacename, n.get('name') + '_qml', False)
            out.write("  " + signature + ";\n")
        out.write(" private:\n")
        out.write("  QQuickItem* api_;\n")
        out.write("};\n\n");


    def write_adaptor_definition(self, interface_el, notifications, request_responses, out):
        iface_name = interface_el.get('name')
        classname = iface_name + 'Adaptor'
        out.write(classname + '::' + classname + "(QObject* parent) : QDBusAbstractAdaptor(parent) {}\n")
        out.write('void ' + classname + "::SetApi(QQuickItem* api) {\n")
        out.write("  api_ = api;\n")
        for n in notifications:
            signame = n.get('name')
            signame = signame[:1].lower() + signame[1:]
            slotname = n.get('name') + '_qml'
            sig_signature = self.make_qml_signal_signature(n, iface_name, signame, True)
            slot_signature = self.make_qml_signal_signature(n, iface_name, slotname, True)
            out.write("  connect(api_, SIGNAL(" + sig_signature + "), this, SLOT(" + slot_signature + "));\n")
        out.write("}\n\n")
        for (request,response) in request_responses:
            in_params = request.findall('param')
            out_params = response.findall('param')
            signature = self.make_method_signature(request, response, iface_name, True)
            out.write(signature + " {\n")
            if out_params:
                param_desc = self.make_param_desc(out_params[0], iface_name)
                param_type = self.qt_param_type(param_desc)
                out.write('  ' + param_type + " ret;\n")
                return_statement = 'return ret'
            else:
                return_statement = 'return'
            out.write("  QVariantMap in_arg;\n");
            out.write("  QVariant out_arg_v;\n");
            for param in in_params:
                param_name = param.get('name')
                out.write("  PutArgToMap(in_arg, \"" + param_name + "\", " + param_name + "_in);\n")
            method_name = request.get('name')[:1].lower() + request.get('name')[1:]
            out.write("  if (!QMetaObject::invokeMethod(api_, \"" + method_name + "\",")
            out.write("Qt::BlockingQueuedConnection, Q_RETURN_ARG(QVariant, out_arg_v), ")
            out.write("Q_ARG(QVariant, QVariant(in_arg)))) {RaiseDbusError(this); " + return_statement + ";}\n")
            out.write("  if (out_arg_v.type() != QVariant::Map) {RaiseDbusError(this); " + return_statement + ";}\n")
            out.write("  QVariantMap out_arg = out_arg_v.toMap();\n")
            for i in range(1, len(out_params)):
                param = out_params[i]
                param_name = param.get('name')
                param_desc = self.make_param_desc(param, iface_name)
                out.write('  if (!GetArgFromMap(out_arg, \"' + param_name + '\", ' + param_name + "_out)) {RaiseDbusError(this); " + return_statement + ";}\n")
            if out_params:
                param_desc = self.make_param_desc(out_params[0], iface_name)
                param_type = self.qt_param_type(param_desc)
                out.write('  if (!GetArgFromMap(out_arg, \"' + param_desc.name + '\", ret)) RaiseDbusError(this);' + "\n")
                out.write("  return ret;\n")
            out.write("}\n\n")
        for n in notifications:
            slotname = n.get('name') + '_qml'
            slot_signature = self.make_qml_signal_signature(n, iface_name, slotname, False, True)
            out.write(slot_signature + " {\n")
            params = n.findall('param')
            for p in params:
                param = self.make_param_desc(p, iface_name)
                param_type = self.qt_param_type(param)
                param_name = 'p_' + param.name
                if param.mandatory:
                    if param.array or (param.type not in ['Integer', 'String', 'Float', 'Boolean'] and not param.enum):
                        out.write('  ' + param_type + ' ' + param_name + ";\n")
                        out.write('  if (!VariantToValue(' + param.name + ', ' + param_name + ")) return;\n")
                else:
                    out.write('  ' + param_type + ' ' + param_name + ";\n")
                    out.write('  ' + param_name + '.presence = !' + param.name + ".isNull();\n")
                    out.write('  if (' + param_name + ".presence) {\n")
                    out.write('    if (!VariantToValue(' + param.name + ', ' + param_name + ".val)) return;\n")
                    out.write("  }\n")
            out.write('  emit ' + n.get('name') + '(')
            for i in range(len(params)):
                param = self.make_param_desc(params[i], iface_name)
                basic_type = (param.type in ['Integer', 'String', 'Float', 'Boolean']) or param.enum
                if param.array or (not param.mandatory) or (not basic_type):
                    param_name = 'p_' + param.name
                else:
                    param_name = param.name
                out.write(param_name)
                if i != len(params) - 1: out.write(', ')
            out.write(");\n")
            out.write("}\n\n")


    def make_dbus_adaptor_declarations(self, out):
        for interface_el in self.el_tree.findall('interface'):
            notifications = self.find_notifications(interface_el)
            request_responses = self.find_request_response_pairs(interface_el)
            if len(notifications) > 0 or len(request_responses) > 0:
                self.write_adaptor_declaration(interface_el, notifications, request_responses, out)


    def make_dbus_adaptor_definitions(self, out):
        for interface_el in self.el_tree.findall('interface'):
            notifications = self.find_notifications(interface_el)
            request_responses = self.find_request_response_pairs(interface_el)
            if len(notifications) > 0 or len(request_responses) > 0:
                self.write_adaptor_definition(interface_el, notifications, request_responses, out)


    def make_dbus_register_metatypes_declaraion(self, out):
        out.write("void RegisterDbusMetatypes();\n")


    def make_dbus_register_metatypes_definition(self, out):
        out.write("void RegisterDbusMetatypes() {\n")
        for (iface, name) in self.structs:
            struct_name = iface + '_' + name
            out.write('qDBusRegisterMetaType<' + struct_name + ">();\n")
            out.write('qDBusRegisterMetaType<OptionalArgument<' + struct_name + "> >();\n")
            out.write('qDBusRegisterMetaType<QList<' + struct_name + "> >();\n")
            out.write('qDBusRegisterMetaType<OptionalArgument<QList<' + struct_name + "> > >();\n")
        out.write("}\n")


    def make_api_adaptors_class(self, out):
        out.write("struct ApiAdaptors {\n")
        interfaces = self.el_tree.findall('interface')
        def filt(iface):
            return self.find_notifications(iface) or self.find_request_response_pairs(iface)
        interfaces = filter(filt, interfaces) 
        for interface_el in interfaces:
            name = interface_el.get('name') + 'Adaptor'
            out.write("  " + name + "* " + name + "_;\n")
        out.write("  ApiAdaptors() :\n")
        for i in range(len(interfaces)):
            name = interfaces[i].get('name') + 'Adaptor'
            out.write("    " + name + "_(NULL)")
            if i <> len(interfaces) - 1: out.write(',')
            out.write("\n")
        out.write("  {}\n")
        out.write("  void Init(QObject* p) {\n")
        for interface_el in interfaces:
            name = interface_el.get('name') + 'Adaptor'
            out.write("    " + name + "_ = new " + name + "(p);\n")
        out.write("  }\n")
        out.write("  void SetApi(QObject* p) {\n")
        for interface_el in interfaces:
            name = interface_el.get('name') + 'Adaptor'
            chname = interface_el.get('name')
            out.write("    " + name + "_->SetApi(p->findChild<QQuickItem*>(\"" + chname + "\"));\n")
        out.write("  }\n")
        out.write("};\n\n")



arg_parser = ArgumentParser()
arg_parser.add_argument('--infile', required=True)
args = arg_parser.parse_args()

header_name = 'qml_dbus.h'
source_name = 'qml_dbus.cc'

in_tree = ElementTree.parse(args.infile)
in_tree_root = in_tree.getroot()

impl = Impl(in_tree_root, 'com.ford.sdl.hmi')

header_out = open(header_name, "w")
source_out = open(source_name, "w")

header_out.write("""/**
 * @file qml_dbus.h
 * @brief Generated QDbus adaptors header file
 *
 * This file is a part of HMI D-Bus layer.
 */
// Copyright (c) 2013, Ford Motor Company
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// Redistributions of source code must retain the above copyright notice, this
// list of conditions and the following disclaimer.
//
// Redistributions in binary form must reproduce the above copyright notice,
// this list of conditions and the following
// disclaimer in the documentation and/or other materials provided with the
// distribution.
//
// Neither the name of the Ford Motor Company nor the names of its contributors
// may be used to endorse or promote products derived from this software
// without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 'A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.

""")
header_out.write("#ifndef SRC_COMPONENTS_DBUS_QML_DBUS_H_\n");
header_out.write("#define SRC_COMPONENTS_DBUS_QML_DBUS_H_\n\n");
header_out.write("#include <QDBusArgument>\n");
header_out.write("#include <QDBusAbstractAdaptor>\n");
header_out.write("#include <QDBusMetaType>\n");
header_out.write("#include <QQuickItem>\n");
header_out.write("#include \"qml_dbus_common.h\"\n\n");
impl.make_dbus_type_declarations(header_out)
impl.make_dbus_adaptor_declarations(header_out)
impl.make_dbus_register_metatypes_declaraion(header_out)
impl.make_api_adaptors_class(header_out)
impl.make_dbus_metatype_declarations(header_out)
header_out.write("#endif // #ifndef SRC_COMPONENTS_DBUS_QML_DBUS_H_\n");

source_out.write("""/**
 * @file qml_dbus.cc
 * @brief Generated QDbus adaptors source file
 *
 * This file is a part of HMI D-Bus layer.
 */
// Copyright (c) 2013, Ford Motor Company
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// Redistributions of source code must retain the above copyright notice, this
// list of conditions and the following disclaimer.
//
// Redistributions in binary form must reproduce the above copyright notice,
// this list of conditions and the following
// disclaimer in the documentation and/or other materials provided with the
// distribution.
//
// Neither the name of the Ford Motor Company nor the names of its contributors
// may be used to endorse or promote products derived from this software
// without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 'A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.

""")
source_out.write("#include \"" + header_name + "\"\n\n");
impl.make_dbus_type_definitions(source_out)
impl.make_dbus_adaptor_definitions(source_out)
impl.make_dbus_register_metatypes_definition(source_out)
