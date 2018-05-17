from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp import http
from openerp.http import request,db_filter
import time
import openerp
import base64, re
from datetime import date
from openerp.exceptions import except_orm, Warning, RedirectWarning
import csv


class payfort_payment_status(http.Controller):


    @http.route([
        '/ticket2721/parent_activeupdate'
    ], type='http', auth="public")
    def check_duplicate_parent_activeupdate(self, **post): 
        
        partner_obj = request.env['res.partner']
        obj_sequence=request.env['ir.sequence']
        

        count = 0        
        #with open('/home/ubuntu/shanky/AIS_student_parent_sheet/ais_parent.csv','r') as e: 
        #with open('/home/ubuntu/shanky/AIS_student_parent_sheet/parent_update.csv','r') as e:
        with open('/home/ubuntu/csv/parent_update.csv','r') as e:
            reader = csv.reader(e)
            
            vals=[row for row in reader]
            
            for val in vals : 
                count+=1;print count
                
                if count==1:
                    continue
#                 if count >2 : 
#                     break
                val=[x.strip() for x in val]

        
                old_id = val[0]
                parent_exist = partner_obj.sudo().search([("old_id","=",old_id),("school_remark","=","AIS PARENT SHEET UPLOADED ON 28AUGUST2016")])
                
                if parent_exist:
                    #print "---EXIST----------"
                    if val[1]  :
                        if val[1]=="True" :
                            active = True
                        else:
                            active = False
                        #import ipdb;ipdb.set_trace()
                        for rec in parent_exist:
                            rec.active = active
                            print "update"
                        
                                                    
                else:
                    parent_exist_inactive = partner_obj.sudo().search([("active","=",False),("old_id","=",old_id),("school_remark","=","AIS PARENT SHEET UPLOADED ON 28AUGUST2016")])
                    if parent_exist_inactive:
                         
                        #print "---EXIST----------"
                        if val[1]  :
                            if val[1]=="True" :
                                active = True
                            else:
                                active = False
                            #import ipdb;ipdb.set_trace()
                            for rec in parent_exist_inactive:
                                rec.active = active
                                print "updated"       
        
        return "success"

    @http.route("/ticket_2829_2831/", auth='none')
    def get_cust_advance_account(self):
        """
        Add Advance account to customer
        -----------------
        :return:
        """
        env = request.env(user=SUPERUSER_ID)
        res_part = env['res.partner']
        count = 0
        for partner in res_part.search([]):
            count += 1; print count
            if not partner.property_account_customer_advance:
                partner.property_account_customer_advance = 678
                print "Updated"

        return "Sucecess"


    @http.route([
        '/ticket2721/student_production'
    ], type='http', auth="public")
    def upload_student_ais_production(self, **post): 

        partner_obj = request.env['res.partner']
        obj_sequence=request.env['ir.sequence']
        class_obj = request.env ['course']
        section_obj = request.env['section']
        country_obj=request.env['res.country']
        religion_obj=request.env['religion']
        count = 0
        
        #with open('/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/ais_student.csv','r') as e:
        with open('/home/ubuntu/csv/ais_student.csv','r') as e: 
            reader = csv.reader(e)
            
            vals=[row for row in reader]
            
            for val in vals :
                values = {}
                count+=1;print count
                if count==1:
                    continue
                
                

                    
#                 if count > 2:
#                     break
#                                 
#                 partner = partner_obj.search([("old_id","=",val[13])])
#                 if not partner : 
#                     import ipdb;ipdb.set_trace()
#                     print "-NOT FOUND-"
# 
#                 print "----------FOUND YOU-----"
#                 continue
                    
                

                val=[x.strip() for x in val]
                
                values["old_id"] = val[0] 
                values["name"] = val[1]
                values["middle_name"] = val[2]
                values["last_name"] = val[3]
                
                if val[6]:
                    
                    classes = class_obj.sudo().search([("code","=",val[6])])
                    if not classes : 
                        
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/no_class.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/no_class.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[6])+'\n')  
                            
                            continue
                    if len(classes)>1 : 
                        
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/multiple_class.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/multiple_class.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[6])+'\n')
                            continue 
                    
                    values["class_id"] = classes.id
                    values["course_id"] = classes.id
                        
                else:
                    
                    #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/extra/no_class.txt", "a") as donefile_new:
                    with open("/home/ubuntu/csv/logs/extra/no_class.txt", "a") as donefile_new:
                        donefile_new.write(str(val[0])+'{}'+str(val[6])+'{}'+str(val[11])+'\n')                        
                    
                
                values["batch_id"]= 3#2015-16             
#                 if count ==14 : 
#                     import ipdb;ipdb.set_trace()     
                if val[8]:
                                    
                    student_section = section_obj.sudo().search([("code","=",val[8])])
                    if not student_section :
                        
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/no_section.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/no_section.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[8])+'\n') 
                            continue 
                    if len(student_section)>1 :
                         
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/multiple_section.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/multiple_section.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[8])+'\n')   
                            continue              
                    if student_section : 
                        
                        values["student_section_id"] = student_section.id
                else:
                    
                    #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/extra/no_section.txt", "a") as donefile_new:
                    with open("/home/ubuntu/csv/logs/extra/no_section.txt", "a") as donefile_new:
                        donefile_new.write(str(val[0])+'{}'+str(val[8])+'{}'+str(val[11])+'\n')                  

                if val[13]:
                        
                    parent = partner_obj.sudo().search([("old_id","=",val[13])])
                    if not parent : 
                        parent = partner_obj.sudo().search([("active","=",False),("old_id","=",val[13])])
                        if not parent:
                            
                            #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/no_parent.txt", "a") as donefile_new:
                            with open("/home/ubuntu/csv/logs/no_parent.txt", "a") as donefile_new:
                                donefile_new.write(str(val[0])+'{}'+str(val[13])+'\n')  
                            continue
                    if len(parent)>1 : 
                        
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/multiple_parent.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/multiple_parent.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[13])+'\n')        
                        continue
                              
                    values["parents1_id"] = parent.id
                else:
                    
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/extra/no_parent.txt", "a") as donefile_new:
                    with open("/home/ubuntu/csv/logs/extra/no_parent.txt", "a") as donefile_new:
                        donefile_new.write(str(val[0])+'{}'+str(val[13])+'{}'+str(val[11])+'\n')                      
                    
                    
                date_of_joining =val[20]
                if date_of_joining : 
                    
                    date_of_joining = date_of_joining.split("/")
                    date_of_joining = date_of_joining[1] +"/" + date_of_joining[0]+"/"+date_of_joining[2]
                    values["date_of_joining"] = date_of_joining
                
                birth_date = val[29]
#                 if count==5515:
#                     import ipdb;ipdb.set_trace()
#                 else:
#                     continue
                if birth_date : 
                    
                    birth_date = birth_date.split("/")
                    birth_date =  birth_date[1] +"/" + birth_date[0]+"/"+birth_date[2]
                    values["birth_date"] = birth_date
                
                student_gender = val[22]
                if student_gender and student_gender=="Male" : 
                    values["gender"] = 'm'
                elif student_gender and student_gender=="Female" : 
                    values["gender"] = 'f'
                else : 
                    print 'no gender'

                values["email"] = val[25]
                
                
                nationality = val[27]
                if nationality:
                    nationality_val = country_obj.sudo().search([("name","=",nationality)])
                    
                    if nationality_val:
                        
                        values["nationality"] = nationality_val.id
                    else:
                        
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/no_nationality_exist.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/no_nationality_exist.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[27])+'\n')

                               
                else:
                        
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/extra/no_nationality_exist.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/extra/no_nationality_exist.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[27])+'{}'+str(val[11])+'\n')
          
                

 
                religion_id = val[28]
                if religion_id:
                    religion_val=religion_obj.sudo().search([("name","=",religion_id)])
                    if religion_val:
                        values["religion_id"] = religion_val.id
                    else:
                        #import ipdb;ipdb.set_trace()
                        
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/invalid_religion.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/invalid_religion.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[28])+'\n') 
       
                        continue                     

                else:
                    
                    #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/extra/invalid_religion1.txt", "a") as donefile_new:
                    with open("/home/ubuntu/csv/logs/extra/invalid_religion1.txt", "a") as donefile_new:
                        donefile_new.write(str(val[0])+'{}'+str(val[28])+'{}'+str(val[11])+'\n')         
                                   
                        

                if val[32]:
                    
                    values["emirates_id"] = val[32]
                if val[39]:
                    values["street"] = val[39]
                
                if val[40]:
                    values["street2"] = val[40]
                
                if val[44]:
                    values["phone"] = val[44]
                    
                if val[53]:
                    values["bus_no"] = val[53]
                    
                
                
#                 if count==951:
#                     import ipdb;ipdb.set_trace()
#                 else:
#                     continue
                if val[52]:
                    if val[52]=="Own":
                        values["transport_type"] = "own"
                    else:
                        values["transport_type"] = "school"
                        
                    
                if val[55]:
                    values["pick_up"] = val[55]
                if val[56]:
                    values["droup_off_pick"] = val[56]
                values["school_remark"] = "AIS STUDENT SHEET UPLOADED ON 28AUGUST2016"
                values["is_student"] = True                    
                    

                #added later
                if val[5]:
                    
                    values["reg_no"] =  val[5]
                if val[9]:
                    
                    shift = val[9]
                    if shift : 
                            
                        if shift=="Morning Batch":
                            values["stud_batch_shift"]="morning"
                        else:
                            values["stud_batch_shift"]="clb"
                    
                admission_date_of_student =val[21]
                if admission_date_of_student : 
                    
                    admission_date_of_student = admission_date_of_student.split("/")
                    admission_date_of_student = admission_date_of_student[1] +"/" + admission_date_of_student[0]+"/"+admission_date_of_student[2]
                    values["admission_date"] = admission_date_of_student



                birth_country = val[30]
                if birth_country:
                    birth_country_val = country_obj.sudo().search([("name","=",birth_country)])
                    if birth_country_val:
                        
                        values["birth_country"] = birth_country_val.id
                    else:
                        
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/no_birthcountry_exist.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/no_birthcountry_exist.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'{}'+str(val[30])+'\n')   
                        continue 
                else:
                    
                    #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/extra/no_birthcountry_exist.txt", "a") as donefile_new:
                    with open("/home/ubuntu/csv/logs/extra/no_birthcountry_exist.txt", "a") as donefile_new:
                        donefile_new.write(str(val[30])+'{}'+str(val[30])+'{}'+str(val[11])+'\n') 
                                         
                                
#                 city = val[31]
#                 if city:
#                     values["city"] = city
                
                passport_no=val[33]       
                if passport_no:
                    values["passport_no"] = passport_no
                    
                
                passport_expiry_date =val[35]
                if passport_expiry_date : 
                    
                    passport_expiry_date = passport_expiry_date.split("/")
                    passport_expiry_date = passport_expiry_date[1] +"/" + passport_expiry_date[0]+"/"+passport_expiry_date[2]
                    values["passport_expiry_date"] = passport_expiry_date 
                
                visa_no = val[36]
                if visa_no :
                    values["visa_no"]=visa_no
                
                visa_expiry_date =  val[38]     
                if visa_expiry_date:
                    visa_expiry_date = visa_expiry_date.split("/")
                    visa_expiry_date = visa_expiry_date[1] +"/" + visa_expiry_date[0]+"/"+visa_expiry_date[2]
                    values["visa_expiry_date"] = visa_expiry_date       


                
                mobile=val[45]
                if mobile:
                    values["mobile"]=mobile
                    
                    
                
                # CREATE STUDENT RECORD
                #import ipdb;ipdb.set_trace()
                student_id = partner_obj.sudo().create(values)
                print "------student created"
                #import ipdb;ipdb.set_trace()
                seq_no = obj_sequence.next_by_id(33)
                
                #ACCOUNTING
                #import ipdb;ipdb.set_trace()
                partner = student_id#partner_obj.sudo().browse(parent_id)
                partner.property_account_receivable = 572
                partner.property_account_payable = 850
                partner.property_account_customer_advance = 678
                partner.re_reg_advance_account =858
                partner.student_id = seq_no
                active = val[11]
                if active : 
                    if val[11] =="True"  :
                        partner.active = True
                        partner.ministry_approved = True
                    else : 
                        partner.active = False

                promoted =val[12]
                if promoted  :
                    
                    if promoted =="True"  :
                        partner.promoted = True
                    else : 
                        partner.promoted = False
        
        return "Successfull"    



    @http.route([
        '/ticket2721/parent_production'
    ], type='http', auth="public")
    def upload_parent_ais_production(self, **post): 
        
        partner_obj = request.env['res.partner']
        obj_sequence=request.env['ir.sequence']
        test_count=0
        
#         with open('/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/ais_parent.csv','r') as e: 
#             reader = csv.reader(e)
#             
#             vals=[row for row in reader]
#             parent_ids_li = []
#             for val in vals : 
#                 test_count+=1;print test_count
#                 #import ipdb;ipdb.set_trace()
#                 if test_count==1:
#                     continue
# #                 if count >2 : 
# #                     break
#                 val=[x.strip() for x in val]
#                 
#                 old_id = val[0]
#                 parent_ids_li.append(old_id)  
#         duplicate_val = [x for x in parent_ids_li if parent_ids_li.count(x)>1]     

        count = 0        
        #with open('/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/ais_parent.csv','r') as e:
        with open('/home/ubuntu/csv/ais_parent.csv','r') as e: 
            reader = csv.reader(e)
            
            vals=[row for row in reader]
            
            for val in vals : 
                count+=1;print count
                
                if count==1:
                    continue
#                 if count >2 : 
#                     break
                val=[x.strip() for x in val]
                
                old_id = val[0]
                parent_exist = partner_obj.sudo().search([("old_id","=",old_id)])
                if parent_exist:
                    print "---EXIST----------"
                    #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/duplicated_parent_ids.txt", "a") as donefile_new:
                    
                    with open("/home/ubuntu/csv/logs/duplicated_parent_ids.txt", "a") as donefile_new:
                        donefile_new.write(str(val[0])+'\n') 
                    continue
                
                else:
                    parent_exist_inactive = partner_obj.sudo().search([("active","=",False),("old_id","=",old_id)])
                    if parent_exist_inactive:
                         
                        print "---EXIST----------"
                        #with open("/home/bista/shanky/IQRA/CSV_UPLOAD/AIS_upload_students_parents/logs/duplicated_parent_ids.txt", "a") as donefile_new:
                        with open("/home/ubuntu/csv/logs/duplicated_parent_ids.txt", "a") as donefile_new:
                            donefile_new.write(str(val[0])+'\n') 
                        continue                    
                    
                    
                name = val[1]
                middle_name = val[2]
                last_name = val[3]
                if val[4]  :
                    if val[4]=="True" :
                        active = True
                    else:
                        active = False
                        
                active = active
                
                parent_profession = val[9]
                mother_name = val[10]
                mother_profession = val[11]
                isd_code = val[12]
                parent_contact = val[13]
                mother_contact = val[14]
                parents_email = val[15]
                parents_office_contact =  val[16]
                mother_office_contact = val[17]
                parent_address = val[18]
                mother_address = val[19]

                school_remark = "AIS PARENT SHEET UPLOADED ON 28AUGUST2016"
                
                is_parent = True
                values = dict (old_id= old_id,name=name,middle_name=middle_name,last_name=last_name,active=active,\
                               parent_profession=parent_profession,mother_profession=mother_profession,\
                               parents_email=parents_email,mother_contact=mother_contact,parent_address=parent_address,\
                               isd_code=isd_code,parent_contact=parent_contact,parents_office_contact=parents_office_contact,\
                               mother_office_contact=mother_office_contact,mother_address=mother_address,\
                               is_parent=is_parent,school_remark=school_remark,mother_name=mother_name)
                # CREATE STUDENT RECORD
                
                parent_id = partner_obj.sudo().create(values)
                print "------parent created"
                seq_no = obj_sequence.next_by_id(34)
                #seq_no = obj_sequence.next_by_id(34) (Live)
                
                #ACCOUNTING
                
                partner = parent_id#partner_obj.sudo().browse(parent_id)
                partner.property_account_receivable =572
                partner.property_account_payable = 850
                partner.property_account_customer_advance = 678
                #partner.active = active
                partner.re_reg_advance_account =858#(Live)
                #import ipdb;ipdb.set_trace()
                partner.parent1_id = seq_no 
                
                #break
        
        return "Successfull"


    @http.route([
        '/ticket2524'
    ], type='http', auth="public", website=True)
    def rectify_partial_payment(self, **post):
        """
        this method rectify parital payment to paid state for invalid record
        """
        
        next_year_pay_obj = request.env ["next.year.advance.fee"]
        partner_obj = request.env["res.partner"]
        reg_obj = request.env["registration"]
        env = request.env(user=SUPERUSER_ID)
        import csv
        count=0
        
        id_to_update=[]
        state=[]
        amount=[]
        reg_ids=[]
        with open("/home/ubuntu/csv/2524_v2.csv", "r") as e:
        #with open('/home/bista/shanky/IQRA/RECTIFY/2016/2524/2524_v2.csv','r') as e: 
            reader = csv.reader(e)
            
            vals=[row for row in reader]
            
            for val in vals :
                count+=1;print count
                val=[x.strip() for x in val]
                
                # SEARCH USERNAME IN ODOO
                
                if val[3] == "Fully Paid" :
                    state.append(val[3])
                    
                    enquiry_no = '/'.join([i for i in val[0],val[1],val[2]])
#                     if enquiry_no =="2016/FS/1139" :
#                         import ipdb;ipdb.set_trace() 
                        
                    student_id = partner_obj.sudo().search([("reg_no","=",enquiry_no)])
                    if not student_id : 
                        with open("/home/ubuntu/csv/logs/logs.txt", "a") as donefile_new:
                        #with open("/home/bista/shanky/IQRA/RECTIFY/2016/2524/logs/logs.txt", "a") as donefile_new:
                            donefile_new.write(str(enquiry_no)+'\n')
                        continue
                            
                    if enquiry_no == "2016/FS/623" :
                         
                        next_yr_record = next_year_pay_obj.sudo().search([("partner_id","=",student_id[0].id),\
                                                ("state","=","fee_unpaid")])
                    else :
                             
                        next_yr_record = next_year_pay_obj.sudo().search([("partner_id","=",student_id[0].id),\
                                                    ("state","=","fee_partial_paid")])
                    if not next_yr_record :
                        with open("/home/ubuntu/csv/logs/logs2.txt", "a") as donefile_new:
                        #with open("/home/bista/shanky/IQRA/RECTIFY/2016/2524/logs/logs2.txt", "a") as donefile_new:
                            donefile_new.write(str(enquiry_no)+'\n')
                        continue
                    if len(next_yr_record) > 1 :
                        with open("/home/ubuntu/csv/logs/logs3.txt", "a") as donefile_new:
                        #with open("/home/bista/shanky/IQRA/RECTIFY/2016/2524/logs/logs3.txt", "a") as donefile_new:
                            donefile_new.write(str(enquiry_no)+str(next_yr_record)+'\n')
                        continue
                         
                        
                    for rec in  next_yr_record : 
                        print "---------pass-----------"
                        id_to_update.append(rec.id)
                        amount.append(rec._get_residual_amount())
                        #continue
                        rec.total_paid_amount =  rec.total_amount
                        rec.state = "fee_paid"
                        regestration_id=reg_obj.sudo().search([("student_id","=",rec.partner_id.id)])
                        if not regestration_id  :
                            with open("/home/ubuntu/csv/logs/logs4.txt", "a") as donefile_new:
                            #with open("/home/bista/shanky/IQRA/RECTIFY/2016/2524/logs/logs4.txt", "a") as donefile_new:
                                donefile_new.write(str(enquiry_no)+str(next_yr_record)+'\n')
                            continue
                        if len(regestration_id)> 1: 
                            with open("/home/ubuntu/csv/logs/logs5.txt", "a") as donefile_new:
                            #with open("/home/bista/shanky/IQRA/RECTIFY/2016/2524/logs/logs5.txt", "a") as donefile_new:
                                donefile_new.write(str(enquiry_no)+str(next_yr_record)+'\n')
                            continue                            
                            
                        reg_ids.append(regestration_id.id)                            
                        regestration_id.fee_status = "academy_fee_pay"      
                        print "---------updated-----------"
                        
                else:
                    continue
            #import ipdb;ipdb.set_trace()
            print len(id_to_update)
            print len(state)
            print len(reg_ids)
            print amount
            print "----over---------"
            return "Success"

                   
                                                 



    def _get_period(self):
        """
        This method is used for getting
        current period.
        -------------------------------
        :return: period id
        """
        env = request.env(user=SUPERUSER_ID)
        context = env.context
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = env['account.period'].find(context=ctx)
        return periods and periods[0] or False

    def get_journal_from_payfort(self):
        """
        This method is use to get payment method
        from payfort master.
        ----------------------------------------
        :return: record set of account.journal object
        """
        env = request.env(user=SUPERUSER_ID)
        active_payforts_rec = env['payfort.config'].sudo().search([('active', '=', 'True')])
        if len(active_payforts_rec) == 1:
            if active_payforts_rec.journal_id.id:
                return active_payforts_rec.journal_id.id
            else:
                return 12
        else:
            return 12

    def _get_currency(self):
        """
        this method use for get account currency.
        -----------------------------------------
        :return: record set of currency.
        """
        env = request.env(user=SUPERUSER_ID)
        # if self._context is None: self._context = {}
        journal_pool = env['account.journal']
        journal_id = env.context.get('journal_id', False)
        if journal_id:
            if isinstance(journal_id, (list, tuple)):
                # sometimes journal_id is a pair (id, display_name)
                journal_id = journal_id[0]
            journal = journal_pool.sudo().browse(journal_id)
            if journal.currency:
                return journal.currency.id
        return env['res.users'].sudo().browse(env.uid).company_id.currency_id.id

    # def re_registration_parent_payment(self, env, re_reg_parent_rec, amount, pay_id, order_id):
    #     """
    #     when parent pay re-registration fee online.
    #     -----------------
    #     :param env:
    #     :param re_reg_parent_rec: re-registration parent payment
    #     :param amount: amount
    #     :param pay_id: payment id
    #     :param order_id:order id
    #     :return:
    #     """
    #     voucher_obj = env['account.voucher']
    #     currency_id = self._get_currency()
    #     c_date = time.strftime('%Y-%m-%d')
    #     t_date = date.today()
    #     # order_id = parent_re_reg_rec.code
    #     period_id = self._get_period().id
    #     journal_id = self.get_journal_from_payfort()
    #     account_id = env['account.journal'].sudo().browse(journal_id).default_debit_account_id.id
    #     total_amount = self.get_orignal_amount(amount)
    #     email_server = env['ir.mail_server']
    #     email_sender = email_server.sudo().search([])
    #     ir_model_data = env['ir.model.data']
    #     template_id = ir_model_data.get_object_reference('bista_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
    #     template_rec = env['email.template'].sudo().browse(template_id)
    #     for student_re_reg_rec in re_reg_parent_rec.student_ids:
    #         if student_re_reg_rec.fee_status != 're_Paid' and total_amount > 0:
    #             student_data = '<table border="2"><b><tr><td>Student Name</td><td>Class-Sec</td><td>Re-Registrition Confirm</td><td>Amount Recived for Re-Registration</td></tr></b>'
    #             student_rec = student_re_reg_rec.name
    #             re_reg_advance_account = student_rec.re_reg_advance_account or False
    #             s_payable_amount = 0.00
    #             if total_amount > student_re_reg_rec.residual:
    #                 s_payable_amount = student_re_reg_rec.residual
    #                 total_amount -= s_payable_amount
    #             else:
    #                 s_payable_amount = total_amount
    #                 total_amount -= s_payable_amount
    #
    #             if s_payable_amount > 0.00:
    #                 voucher_data = {
    #                     'period_id': period_id,
    #                     'account_id': account_id,
    #                     'partner_id': student_rec.id,
    #                     'journal_id': journal_id,
    #                     'currency_id': currency_id,
    #                     'reference': student_re_reg_rec.code,
    #                     'amount': s_payable_amount,
    #                     'type': 'receipt' or 'payment',
    #                     'state': 'draft',
    #                     'pay_now': 'pay_later',
    #                     'name': '',
    #                     'date': c_date,
    #                     'company_id': 1,
    #                     'tax_id': False,
    #                     'payment_option': 'without_writeoff',
    #                     'comment': _('Write-Off'),
    #                     'advance_account_id':re_reg_advance_account.id or student_rec.property_account_customer_advance.id or False,
    #                     'payfort_payment_id' : pay_id,
    #                     'payfort_pay_date' : t_date,
    #                     're_reg_fee' : True,
    #                 }
    #                 voucher_obj_exist = voucher_obj.sudo().search([('partner_id','=',student_rec.id),
    #                                                                ('payfort_payment_id','=',pay_id,)])
    #                 if not voucher_obj_exist.id:
    #                     s_voucher_rec = voucher_obj.sudo().create(voucher_data)
    #
    #                     # update on re-registration student
    #                     student_re_reg_rec.total_paid_amount += s_payable_amount
    #                     if student_re_reg_rec.residual <= 0:
    #                         student_re_reg_rec.fee_status = 're_Paid'
    #                         student_re_reg_rec.name.re_reg_next_academic_year = 'yes'
    #                     elif student_re_reg_rec.total_paid_amount < student_re_reg_rec.total_amount and student_re_reg_rec.total_paid_amount != 0.00:
    #                         student_re_reg_rec.fee_status = 're_partially_paid'
    #                         student_re_reg_rec.name.re_reg_next_academic_year = 'yes'
    #
    #                     # Add Journal Entries
    #                     s_voucher_rec.button_proforma_voucher()
    #
    #                     self.sudo().create_attachment_re_reg_payment_receipt(s_voucher_rec,student_re_reg_rec)
    #                     # Send mail to Parent For Payment Recipt
    #                     student_data += '<tr><td>%s</td><td>%s</td><td>Yes</td><td>%s</td></tr></table>'%(
    #                         student_re_reg_rec.name.name,student_re_reg_rec.next_year_course_id.name,s_payable_amount)
    #                     template_id = ir_model_data.get_object_reference('bista_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
    #                     template_rec = env['email.template'].sudo().browse(template_id)
    #                     template_rec.write({
    #                         'email_to': student_re_reg_rec.name.parents1_id.parents_email,
    #                         'email_from': email_sender.smtp_user,
    #                         'email_cc': 'Erpemails_ais@iqraeducation.net',
    #                         'body_html': '<div><p>Dear, %s </p><br/>'
    #                                          '<p>Thank you for completing the re-registration process by paying an amount of %s and'
    #                                          ' confiriming a place for your child(ren) in the next academic year.'
    #                                          ' Please find the receipt herewith attached for the payment made for the following students:</p>'
    #                                          '<br/>'
    #                                          '<p>%s</p>'
    #                                          '<p>The amount paid towards re-registration is collected as advanced and will be adjusted in next year academic fee.</p>'
    #                                          '<p>Thank you for your prompt response and confirming a seat for your child(ren) in the next academic year with us.'
    #                                          ' We wish your child(ren) better prospects in the next grade and together we will ensure the best of learning for them.</p>'
    #                                          '<p>Best Regards'
    #                                          '<br/><br/>Registrar, The Apple International School, Dubai'
    #                                          '<br/>Email : registrar.apple@iqraeducation.net'
    #                                          '<br/>Link : http://www.apple.iqraeducation.net'
    #                                          '<br>Phone: +971 4 263 8989'
    #                                          '<br/>Fax : +971 4 2619554</p>'%(student_re_reg_rec.name.parents1_id.name,s_payable_amount,student_data)
    #                     })
    #                     template_rec.send_mail(s_voucher_rec.id, force_send=False)
    #
    #     flag_fee_status = True
    #     for student_fee_status in re_reg_parent_rec.student_ids:
    #         if student_fee_status.fee_status == 're_unpaid':
    #             flag_fee_status = False
    #     if flag_fee_status == True:
    #         re_reg_parent_rec.come_to_confirm()
    #
    #     if total_amount > 0.00:
    #         # parent pay amount in advance
    #         partner_rec = re_reg_parent_rec.name
    #         parent_voucher_data = {
    #                     'period_id': period_id,
    #                     'account_id': account_id,
    #                     'partner_id': partner_rec.id,
    #                     'journal_id': journal_id,
    #                     'currency_id': currency_id,
    #                     'reference': re_reg_parent_rec.code,
    #                     'amount': total_amount,
    #                     'type': 'receipt' or 'payment',
    #                     'state': 'draft',
    #                     'pay_now': 'pay_later',
    #                     'name': '',
    #                     'date': c_date,
    #                     'company_id': 1,
    #                     'tax_id': False,
    #                     'payment_option': 'without_writeoff',
    #                     'comment': _('Write-Off'),
    #                     'advance_account_id':partner_rec.property_account_customer_advance.id,
    #                     're_reg_fee' : True,
    #                     'payfort_payment_id' : pay_id,
    #                     'payfort_pay_date' : t_date,
    #                     # 'invoice_id':inv_obj.id,
    #                 }
    #         p_voucher_rec_exist = voucher_obj.sudo().search([('partner_id','=',partner_rec.id),
    #                                                          ('payfort_payment_id','=',pay_id)])
    #         if not p_voucher_rec_exist.id:
    #             p_voucher_rec = voucher_obj.sudo().create(parent_voucher_data)
    #
    #             # Add Journal Entries
    #             p_voucher_rec.button_proforma_voucher()
    #
    #             # template_rec.write({
    #             #     'email_to': partner_rec.parents_email,
    #             #     'email_from': email_sender.smtp_user,
    #             #     'body_html': '<div><p>Dear, %s </p><br/>'
    #             #                      '<p>Thank you for completing the re-registration process by paying an amount of %s and'
    #             #                      ' confiriming a place for your child(ren) in the next academic year.'
    #             #                      ' Please find the receipt herewith attached for the payment made.</p>'
    #             #                      '<p>The amount paid towards re-registration is collected as advanced and will be adjusted in next year academic fee.</p>'
    #             #                      '<p>Thank you for your prompt response and confirming a seat for your child(ren) in the next academic year with us.'
    #             #                      ' We wish your child(ren) better prospects in the next grade and together we will ensure the best of learning for them.</p>'
    #             #                      '</br/>Best Regards'
    #             #                      '<br/>Registrar, The Indian Academy, Dubai'
    #             #                      '<br/>Email : registrar.tiadxb@iqraeducation.net'
    #             #                      '<br/>Link : http://www.indianacademydubai.com'
    #             #                      '<br/>Phone : +971 04 2646746, +971 04 2646733, Toll Free: 800 INDIAN (463426)'
    #             #                      '<br/>Fax : +971 4 2644501'%(partner_rec.name,total_amount)
    #             # })
    #             # template_rec.send_mail(p_voucher_rec.id, force_send=False)

    def next_year_advance_payment(self,env,next_year_advance_fee_rec,order_id,amount,pay_id):
        """
        This method use to online payment for next acdemic year in Advance.
        --------------------------------------------------------------------
        :param env: SUPERUSER object
        :param next_year_advance_fee_rec: record set of next year adv payment object
        :param order_id: unique order id
        :param amount: advance payment amount
        :return:
        """
        voucher_obj = env['account.voucher']
        partner_id = next_year_advance_fee_rec.partner_id
        t_date = date.today()
        journal_id = self.get_journal_from_payfort()
        period_id = self._get_period().id
        account_id = env['account.journal'].sudo().browse(journal_id).default_debit_account_id.id
        total_amount = self.get_orignal_amount(amount)
        currency_id = self._get_currency()
        voucher_data = {
                'period_id': period_id,
                'account_id': account_id,
                'partner_id': partner_id.id,
                'journal_id': journal_id,
                'currency_id': currency_id,
                'reference': order_id,
                'amount': total_amount,
                'type': 'receipt' or 'payment',
                'state': 'draft',
                'pay_now': 'pay_later',
                'name': '',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': 1,
                'tax_id': False,
                'payment_option': 'without_writeoff',
                'comment': _('Write-Off'),
                'payfort_payment_id' : pay_id,
                'payfort_pay_date' : t_date,
        		'advance_account_id':partner_id.property_account_customer_advance.id,
            }
        voucher_id_exist = voucher_obj.sudo().search([('partner_id','=',partner_id.id),
                                                      ('payfort_payment_id','=',pay_id)])
        if not voucher_id_exist.id:
            voucher_id = voucher_obj.sudo().create(voucher_data)

            # Add Journal Entries with Advance Acc.
            voucher_id.button_proforma_voucher()

            next_year_advance_fee_rec.total_paid_amount += total_amount

            if next_year_advance_fee_rec.total_amount <= next_year_advance_fee_rec.total_paid_amount:
                next_year_advance_fee_rec.state = 'fee_paid'
                next_year_advance_fee_rec.reg_id.fee_status = 'academy_fee_pay'
                next_year_advance_fee_rec.reg_id.acd_pay_id = str(pay_id)
                next_year_advance_fee_rec.reg_id.acd_trx_date = t_date
            elif next_year_advance_fee_rec.total_paid_amount < next_year_advance_fee_rec.total_amount and next_year_advance_fee_rec.total_paid_amount != 0.00:
                next_year_advance_fee_rec.state = 'fee_partial_paid'
                next_year_advance_fee_rec.reg_id.fee_status = 'academy_fee_partial_pay'
                next_year_advance_fee_rec.reg_id.acd_pay_id = str(pay_id)
                next_year_advance_fee_rec.reg_id.acd_trx_date = t_date
            next_year_advance_fee_rec.payment_ids = [(4,voucher_id.id)]
            next_year_advance_fee_rec.journal_ids = [(4,journal_id)]
            next_year_advance_fee_rec.journal_id = journal_id

            # send mail to perent with fee receipt
            email_server = env['ir.mail_server']
            email_sender = email_server.sudo().search([])
            ir_model_data = env['ir.model.data']
            template_id = ir_model_data.get_object_reference('bista_edu','email_template_academic_fee_receipt_paid')[1]
            template_rec = env['email.template'].sudo().browse(template_id)
            template_rec.sudo().write(
            {'email_to': next_year_advance_fee_rec.partner_id.parents1_id.parents_email, 'email_from': email_sender.smtp_user, 'email_cc': 'Erpemails_ais@iqraeducation.net'})
            template_rec.send_mail(voucher_id.id, force_send=False)
        return True

    def get_orignal_amount(self,amount):
        """
        this method use to convert orignal amount
        ---------------------------------------------
        :param amount: get amount from payfort link
        :return: return orignal amount of payment.
        """
        env = request.env(user=SUPERUSER_ID)
        active_payforts_rec = env['payfort.config'].sudo().search([('active', '=', 'True')])
        amount = float(amount)
        if len(active_payforts_rec) == 1:
            # divide by 100
            # amount /= 100.00
            # remove Transport charge
            if active_payforts_rec.transaction_charg_amount >= 0:
                transaction_charg_amount = active_payforts_rec.transaction_charg_amount
            else:
                transaction_charg_amount = 0.50
            amount -= transaction_charg_amount
            # removed payfort charge amount
            if active_payforts_rec.charge >= 0:
                dummy_amount = 100.00+active_payforts_rec.charge
                act_amount=round(((amount/dummy_amount)*100.00),2)
            else:
                dummy_amount = 100.00+2.10
                act_amount=round(((amount/dummy_amount)*100.00),2)
            return act_amount
        else:
            # amount /= 100
            amount -= 0.50
            dummy_amount = 100.00+2.10
            act_amount=round(((amount/dummy_amount)*100.00),2)
            return act_amount

    def resend_academic_fee_payment(self, voucher_rec, amount, env, pay_id):
        """
        This method use when fee payment from resend payfort
        link, pay from parent.
        hear, already create voucher with 0.00 amount of parent.
        ------------------------------------------------------------
        :param voucher_rec: parent voucher record set with 0.00 amount
        :param amount: amount to pay from parent
        :param env: environment object
        :param payment_id: unique payment id genaret from payfort payment,
        :return:
        """
        journal_id = self.get_journal_from_payfort()
        voucher_line_obj = env['account.voucher.line']
        date = time.strftime('%Y-%m-%d')
        # assign payble amount to voucher
        if len(voucher_rec) == 1 and amount != 0:
            amount = float(amount)
            update_amount = self.get_orignal_amount(amount)
            voucher_rec.amount = update_amount
        for voucher in voucher_rec:
            voucher.sudo().write({'payfort_payment_id' : pay_id,'journal_id' : journal_id})
            res = voucher.onchange_partner_id(voucher.partner_id.id, journal_id, float(amount), voucher.currency_id.id,
                                              voucher.type, date)

            advance_amount = 0.00
            for line_data in res['value']['line_dr_ids']:
                voucher_lines = {
                    'move_line_id': line_data['move_line_id'],
                    'amount':line_data['amount_unreconciled'],
                    'name': line_data['name'],
                    'amount_unreconciled': line_data['amount_unreconciled'],
                    'type': line_data['type'],
                    'amount_original': line_data['amount_original'],
                    'account_id': line_data['account_id'],
                    'voucher_id': voucher.id,
                    'reconcile': True
                }
                advance_amount += line_data['amount_unreconciled']
                voucher_line_obj.sudo().create(voucher_lines)
            amount += advance_amount
            for line_data in res['value']['line_cr_ids']:
                if amount > 0:
                    set_amount = line_data['amount_unreconciled']
                    if amount <= set_amount:
                        set_amount = amount
                    reconcile = False
                    voucher_lines = {
                        'move_line_id': line_data['move_line_id'],
                        'name': line_data['name'],
                        'amount_unreconciled': line_data['amount_unreconciled'],
                        'type': line_data['type'],
                        'amount_original': line_data['amount_original'],
                        'account_id': line_data['account_id'],
                        'voucher_id': voucher.id,
                        'reconcile': True
                    }
                    voucher_line_rec = voucher_line_obj.sudo().create(voucher_lines)
                    reconsile_vals = voucher_line_rec.onchange_amount(set_amount,line_data['amount_unreconciled'])
                    voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
                    if voucher_line_rec.reconcile:
                        amount_vals = voucher_line_rec.onchange_reconcile(voucher_line_rec.reconcile,line_data['amount_original'],set_amount)
                        voucher_line_rec.amount = amount_vals['value']['amount']
                    else:
                        voucher_line_rec.amount = set_amount
                    amount -= set_amount

            # Validate voucher (Add Journal Entries)
            voucher.button_proforma_voucher()

            # send mail to perent with fee recipt
            email_server = env['ir.mail_server']
            email_sender = email_server.sudo().search([])
            ir_model_data = env['ir.model.data']
            template_id = ir_model_data.get_object_reference('bista_edu','email_template_academic_fee_receipt_paid')[1]
            template_rec = env['email.template'].sudo().browse(template_id)
            template_rec.sudo().write(
            {'email_to': voucher.partner_id.parents_email, 'email_from': email_sender.smtp_user, 'email_cc': 'Erpemails_ais@iqraeducation.net'})
            template_rec.send_mail(voucher.id, force_send=False)

    @http.route([
        '/show_payment_status'
    ], type='http', auth="public", website=True)
    def show_payment_status(self, **post):
        """
        This method use When Online Payment using Payfot getway.
        ----------------------------------------------------------
        :param post:
        :return:it redirect thankyou page if transactions success
                otherwise redirect to transactions fail page.
        """
        env = request.env(user=SUPERUSER_ID)
        try:
            if post['STATUS'] == '9':
                pay_id = post['PAYID']
                return request.render("website_student_enquiry.thankyou_reg_fee_paid", {
                        'pay_id': pay_id})
            else:
                return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
        except:
            return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})

    @http.route([
        '/show_acd_payment'
    ], type='http', auth="public", website=True)
    def show_acd_payment(self, **post):
        """
        This method use When Online Payment using Payfot getway.
        ----------------------------------------------------------
        :param post:
        :return:it redirect thankyou page if transactions success
                otherwise redirect to transactions fail page.
        """
        env = request.env(user=SUPERUSER_ID)
        voucher_pool = env['account.voucher']
        voucher_line_pool = env['account.voucher.line']
        journal_id = self.get_journal_from_payfort()
        try:
            reg_ids = env['registration'].sudo().search([('enquiry_no', '=', post['orderID'])])
            invoice_ids = env['account.invoice'].sudo().search([('number', '=', post['orderID'])])
            voucher_rec = env['account.voucher'].sudo().search(
                [('payfort_type', '=', True), ('payfort_link_order_id', '=', post['orderID'])])
            next_year_advance_fee_rec = env['next.year.advance.fee'].sudo().search([('order_id', '=', post['orderID'])])
            # re_registration_parent_rec = env['re.reg.waiting.responce.parents'].sudo().search([('code','=',post['orderID'])],
            #                                                                               limit=1)
        except:
            return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
        # registration fee payment
        if len(reg_ids) > 0:
            pay_id = ''
            if post['STATUS'] == '9':
                for each in reg_ids:
                    each.fee_status = 'reg_fee_pay'
                    each.pay_id = post['PAYID']
                    datestring = post['TRXDATE']
                    datestring = datestring[:6] + '20' + datestring[6:]
                    c = time.strptime(datestring, "%m/%d/%Y")
                    c1 = time.strftime("%Y-%m-%d", c)
                    each.trx_date = c1
                    pay_id = each.pay_id
                    jounral_dict1 = {}
                    jounral_dict2 = {}
                    account_move_obj = env['account.move']
                    exist_stu_fee = account_move_obj.sudo().search_count([('ref', '=', each.enquiry_no)])
                    # journal_id = env['account.journal'].search([('name','=','Online Payment'),('type','=','bank')],limit=1)
                    # if journal_id.id:

                    account_move_obj = env['account.move']
                    account_id = env['account.account'].sudo().search([('code', '=', '402050')], limit=1)

                    if exist_stu_fee == 0:
                        for student_fee_rec in each.reg_fee_line:
                            if student_fee_rec.amount:
                                full_name = str(each.name or '') + ' ' + str(each.middle_name or '') + ' ' + str(
                                    each.last_name or '')
                                jounral_dict1.update({'name': full_name, 'debit': student_fee_rec.amount})
                                jounral_dict2.update(
                                    {'name': full_name, 'credit': student_fee_rec.amount, 'account_id': account_id.id})
                        move_id = account_move_obj.sudo().create(
                            {'journal_id': journal_id, 'line_id': [(0, 0, jounral_dict1), (0, 0, jounral_dict2)],
                             'ref': each.enquiry_no})
                        each.reg_fee_receipt = move_id.id

                    # code for sending fee receipt to student
                    mail_obj = env['mail.mail']
                    email_server = env['ir.mail_server']
                    email_sender = email_server.sudo().search([])
                    ir_model_data = env['ir.model.data']
                    template_id = \
                    ir_model_data.get_object_reference('bista_edu', 'email_template_registration_receipt')[1]
                    template_rec = env['email.template'].sudo().browse(template_id)
                    template_rec.sudo().write({'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': 'Erpemails_ais@iqraeducation.net'})
                    template_rec.send_mail(each.id, force_send=True)
                    return request.render("website_student_enquiry.thankyou_reg_fee_paid", {
                        'pay_id': pay_id})
            else:
                return request.render("website_student_enquiry.thankyou_reg_fee_fail", {
                })

        # invoice payment
        if len(invoice_ids) > 0:
            if post['STATUS'] == '9':
                datestring = post['TRXDATE']
                # amount = float(post['amount'])
                datestring = datestring[:6] + '20' + datestring[6:]
                c = time.strptime(datestring, "%m/%d/%Y")
                tran_date = time.strftime("%Y-%m-%d", c)
                reg_obj = env['registration']
                inv_id = ""
                c_amount = post['amount']
                for inv_obj in invoice_ids:
                    if inv_obj.state != 'open':
                        # -----------------------------------------------------------------
                        amount = self.get_orignal_amount(c_amount)
                        journal_rec = env['account.journal'].sudo().browse(journal_id)
                        voucher_data = {
                            'period_id': inv_obj.period_id.id,
                            'account_id': journal_rec.default_debit_account_id.id,
                            'partner_id': inv_obj.partner_id.id,
                            'journal_id': journal_rec.id,
                            'currency_id': inv_obj.currency_id.id,
                            'reference': post['orderID'],  # payplan.name +':'+salesname
                            'amount': amount,
                            'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            'payfort_payment_id' : post['PAYID'],
                            'payfort_pay_date' : tran_date,
                        }
                        voucher_pool_exist = voucher_pool.sudo().search([('partner_id' ,'=', inv_obj.partner_id.id),
                                                                         ('payfort_payment_id' ,'=', post['PAYID'])])
                        if voucher_pool_exist.id:
                            return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                'pay_id': post['PAYID']})
                        else:
                            voucher_id = voucher_pool.sudo().create(voucher_data)
                            # return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
                            voucher_id.button_proforma_voucher()
                        # payment date and payment id store in invoice
                        inv_obj.payfort_pay_date = tran_date
                        inv_obj.payfort_payment_id = post['PAYID']

                        reg_ids = reg_obj.sudo().search([('student_id', '=', inv_obj.partner_id.id)])

                        # code for sending fee receipt to student
                        if len(reg_ids) > 0:
                            for each in reg_ids:
                                each.fee_status = 'academy_fee_pay'
                                each.acd_pay_id = post['PAYID']
                                each.acd_trx_date = tran_date
                                email_server = env['ir.mail_server']
                                email_sender = email_server.sudo().search([])
                                ir_model_data = env['ir.model.data']
                                template_id = ir_model_data.get_object_reference(
                                    'bista_edu',
                                    'email_template_academic_fee_receipt_paid')[1]
                                template_rec = env['email.template'].sudo().browse(template_id)
                                template_rec.sudo().write(
                                    {'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': 'Erpemails_ais@iqraeducation.net'})
                                template_rec.send_mail(voucher_id.id)
                        return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                            'pay_id': post['PAYID']})
                        # --------------------------------------------------------------------


                    else:
                        amount = self.get_orignal_amount(c_amount)
                        journal_rec = env['account.journal'].sudo().browse(journal_id)
                        voucher_data = {
                            'period_id': inv_obj.period_id.id,
                            'account_id': journal_rec.default_debit_account_id.id,
                            'partner_id': inv_obj.partner_id.id,
                            'journal_id': journal_rec.id,
                            'currency_id': inv_obj.currency_id.id,
                            'reference': inv_obj.name,  # payplan.name +':'+salesname
                            'amount': amount,
                            'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            'payfort_payment_id' : post['PAYID'],
                            'payfort_pay_date' : tran_date,
                        }
                        voucher_pool_exist = voucher_pool.sudo().search([('partner_id' ,'=', inv_obj.partner_id.id),
                                                                         ('payfort_payment_id' ,'=', post['PAYID'])])
                        if voucher_pool_exist.id:
                            return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                'pay_id': post['PAYID']})
                        else:
                            voucher_id = voucher_pool.sudo().create(voucher_data)
                            date = time.strftime('%Y-%m-%d')
                            if voucher_id:
                                res = voucher_id.onchange_partner_id(inv_obj.partner_id.id, journal_id,
                                                                     inv_obj.amount_total,
                                                                     inv_obj.currency_id.id, inv_obj.type, date)
                                advance_amount = 0.00
                                for line_data in res['value']['line_dr_ids']:
                                    voucher_lines = {
                                        'move_line_id': line_data['move_line_id'],
                                        'amount':line_data['amount_unreconciled'],
                                        'name': line_data['name'],
                                        'amount_unreconciled': line_data['amount_unreconciled'],
                                        'type': line_data['type'],
                                        'amount_original': line_data['amount_original'],
                                        'account_id': line_data['account_id'],
                                        'voucher_id': voucher_id.id,
                                        'reconcile': True
                                    }
                                    advance_amount += line_data['amount_unreconciled']
                                    voucher_line_pool.sudo().create(voucher_lines)
                                amount += advance_amount
                                for line_data in res['value']['line_cr_ids']:
                                    # if not line_data['amount']:
                                    #     continue
                                    # name = line_data['name']
                                    if line_data['name'] in [inv_obj.number]:
                                        if amount > 0:
                                            print "AMOUNT",amount
                                            set_amount = line_data['amount_unreconciled']
                                            if amount <= set_amount:
                                                set_amount = amount
                                            reconcile = False
                                            voucher_lines = {
                                                'move_line_id': line_data['move_line_id'],
                                                'name': line_data['name'],
                                                'amount_unreconciled': line_data['amount_unreconciled'],
                                                'type': line_data['type'],
                                                'amount_original': line_data['amount_original'],
                                                'account_id': line_data['account_id'],
                                                'voucher_id': voucher_id.id,
                                                'reconcile': True
                                            }
                                            voucher_line_rec = voucher_line_pool.sudo().create(voucher_lines)
                                            reconsile_vals = voucher_line_rec.onchange_amount(set_amount,line_data['amount_unreconciled'])
                                            voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
                                            if voucher_line_rec.reconcile:
                                                amount_vals = voucher_line_rec.onchange_reconcile(voucher_line_rec.reconcile,line_data['amount_original'],set_amount)
                                                voucher_line_rec.amount = amount_vals['value']['amount']
                                            else:
                                                voucher_line_rec.amount = set_amount
                                            amount -= set_amount

  

                                # Add Journal Entries
                                voucher_id.button_proforma_voucher()
                                # payment date and payment id store in invoice
                                inv_obj.payfort_pay_date = tran_date
                                inv_obj.payfort_payment_id = post['PAYID']

                                partner_id = inv_obj.partner_id
                                reg_ids = reg_obj.sudo().search([('student_id', '=', partner_id.id)])

                                # code for sending fee receipt to student
                                if len(reg_ids) > 0:
                                    for each in reg_ids:
                                        each.fee_status = 'academy_fee_pay'
                                        each.acd_pay_id = post['PAYID']
                                        each.acd_trx_date = tran_date
                                        email_server = env['ir.mail_server']
                                        email_sender = email_server.sudo().search([])
                                        ir_model_data = env['ir.model.data']
                                        template_id = ir_model_data.get_object_reference(
                                            'bista_edu',
                                            'email_template_academic_fee_receipt_paid')[1]
                                        template_rec = env['email.template'].sudo().browse(template_id)
                                        template_rec.sudo().write(
                                            {'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': 'Erpemails_ais@iqraeducation.net'})
                                        template_rec.send_mail(voucher_id.id, force_send=True)

                                        return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                            'pay_id': post['PAYID']})
            else:
                return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
                })

        # for re-send academic link
        if len(voucher_rec) > 0:
            if post['STATUS']=='9':
                self.resend_academic_fee_payment(voucher_rec=voucher_rec,
                                                 amount=post.get('amount'),
                                                 env=env,
                                                 pay_id = post['PAYID'])
                return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                'pay_id': post['PAYID']})
            else:
                return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
                      })

        # for next year advance fee payment
        if len(next_year_advance_fee_rec) > 0:
            if post['STATUS']=='9':
                order_id = post['orderID']
                c_amount = post['amount']
                payment_id = post['PAYID']
                voucher_obj = env['account.voucher']
                voucher_rec = voucher_obj.sudo().search([('payfort_payment_id','=',payment_id),('reference','=',order_id)],
                                                 limit=1)
                if not voucher_rec.id:
                    self.next_year_advance_payment(env=env,
                                                   next_year_advance_fee_rec=next_year_advance_fee_rec,
                                                   order_id=order_id,
                                                   amount=c_amount,
                                                   pay_id = payment_id)

                    return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                    'pay_id':post['PAYID']})
                else:
                    return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                    'pay_id':post['PAYID']})
            else:
                return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})

        # re-registration fee payment
        # if len(re_registration_parent_rec) > 0:
        #     if post['STATUS']=='9':
        #         order_id = post['orderID']
        #         c_amount = post['amount']
        #         payment_id = post['PAYID']
        #         self.re_registration_parent_payment(env=env,
        #                                             re_reg_parent_rec = re_registration_parent_rec,
        #                                             amount=c_amount,
        #                                             pay_id = payment_id,
        #                                             order_id = order_id,
        #                                             )
        #         return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
        #         'pay_id': post['PAYID']})
        #     else:
        #         return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
