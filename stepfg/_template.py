import datetime
import re


def _line_index(line):
    m = re.search(r'#(.+?)=', line)
    return 0 if m is None else int(m.group(1))


def step_header(filename='part_out.stp'):
    d = datetime.datetime.now()
    lines = [
        "ISO-10303-21;",
        "HEADER;",
        "FILE_DESCRIPTION(('none'),'2;1');",
        "",
        "FILE_NAME('" + filename + "','none',('none'),('none'),"
        "'none','none','none');",
        "",
        "FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));",
        "",
        "ENDSEC;",
        "DATA;",
        "#1=APPLICATION_CONTEXT('configuration controlled 3D design of"
        " mechanical parts and assemblies') ;",
        "#2=MECHANICAL_CONTEXT(' ',#1,'mechanical') ;",
        "#3=DESIGN_CONTEXT(' ',#1,'design') ;",
        "#4=APPLICATION_PROTOCOL_DEFINITION('international standard',"
        "'config_control_design',1994,#1) ;",
        "#5=PRODUCT('Part1','','',(#2)) ;",
        "#6=PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('',' '"
        ",#5,.NOT_KNOWN.) ;",
        "#7=PRODUCT_CATEGORY('part',$) ;",
        "#8=PRODUCT_RELATED_PRODUCT_CATEGORY('detail',$,(#5)) ;",
        "#9=PRODUCT_CATEGORY_RELATIONSHIP(' ',' ',#7,#8) ;",
        "#10=COORDINATED_UNIVERSAL_TIME_OFFSET(0,0,.AHEAD.) ;",
        "#11=CALENDAR_DATE(" + str(d.year) + "," + str(d.month) + ","
        + str(d.day) + ") ;",
        "#12=LOCAL_TIME(" + str(d.hour) + "," + str(d.minute) + ","
        + str(d.second) + ".,#10) ;",
        "#13=DATE_AND_TIME(#11,#12) ;",
        "#14=PRODUCT_DEFINITION('',' ',#6,#3) ;",
        "#15=SECURITY_CLASSIFICATION_LEVEL('unclassified') ;",
        "#16=SECURITY_CLASSIFICATION(' ',' ',#15) ;",
        "#17=DATE_TIME_ROLE('classification_date') ;",
        "#18=CC_DESIGN_DATE_AND_TIME_ASSIGNMENT(#13,#17,(#16)) ;",
        "#19=APPROVAL_ROLE('APPROVER') ;",
        "#20=APPROVAL_STATUS('not_yet_approved') ;",
        "#21=APPROVAL(#20,' ') ;",
        "#22=PERSON(' ',' ',' ',$,$,$) ;",
        "#23=ORGANIZATION(' ',' ',' ') ;",
        "#24=PERSONAL_ADDRESS(' ',' ',' ',' ',' ',' ',' ',' ',' ',"
        "' ',' ',' ',(#22),' ') ;",
        "#25=PERSON_AND_ORGANIZATION(#22,#23) ;",
        "#26=PERSON_AND_ORGANIZATION_ROLE('classification_officer') ;",
        "#27=CC_DESIGN_PERSON_AND_ORGANIZATION_ASSIGNMENT(#25,#26,"
        "(#16)) ;",
        "#28=DATE_TIME_ROLE('creation_date') ;",
        "#29=CC_DESIGN_DATE_AND_TIME_ASSIGNMENT(#13,#28,(#14)) ;",
        "#30=CC_DESIGN_APPROVAL(#21,(#16,#6,#14)) ;",
        "#31=APPROVAL_PERSON_ORGANIZATION(#25,#21,#19) ;",
        "#32=APPROVAL_DATE_TIME(#13,#21) ;",
        "#33=CC_DESIGN_PERSON_AND_ORGANIZATION_ASSIGNMENT(#25,#34,"
        "(#6)) ;",
        "#34=PERSON_AND_ORGANIZATION_ROLE('design_supplier') ;",
        "#35=CC_DESIGN_PERSON_AND_ORGANIZATION_ASSIGNMENT(#25,#36,"
        "(#6,#14)) ;",
        "#36=PERSON_AND_ORGANIZATION_ROLE('creator') ;",
        "#37=CC_DESIGN_PERSON_AND_ORGANIZATION_ASSIGNMENT(#25,#38,"
        "(#5)) ;",
        "#38=PERSON_AND_ORGANIZATION_ROLE('design_owner') ;",
        "#39=CC_DESIGN_SECURITY_CLASSIFICATION(#16,(#6)) ;",
        "",
        "#40=PRODUCT_DEFINITION_SHAPE(' ',' ',#14) ;",
        "#41=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.)) ;",
        "#42=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.)) ;",
        "#43=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT()) ;",
        "#44=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.005),#41,"
        "'distance_accuracy_value','CONFUSED CURVE"
        " UNCERTAINTY') ;",
        "#45=(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
        "GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#44))"
        "GLOBAL_UNIT_ASSIGNED_CONTEXT((#41,#42,#43))"
        "REPRESENTATION_CONTEXT(' ',' ')) ;",
        "",
        "#46=CARTESIAN_POINT(' ',(0.,0.,0.)) ;",
        "#47=AXIS2_PLACEMENT_3D(' ',#46,$,$) ;",
        "#48=SHAPE_REPRESENTATION(' ',(#47),#45) ;",
        "#49=SHAPE_DEFINITION_REPRESENTATION(#40,#48) ;",
        "",
        "/* Part Specification */",
        "",
        "ENDSEC;",
        "END-ISO-10303-21;",
    ]
    file_array = [i + "\n" for i in lines]
    index1 = file_array.index("/* Part Specification */\n")
    initial_work_array = [k for k in file_array if k.startswith('#')]
    highest_index = _line_index(
        sorted(initial_work_array, key=_line_index)[-1]
    )
    return file_array, index1, highest_index
