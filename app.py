import os
from flask import Flask, render_template, request, redirect, json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, and_
from flask_sqlalchemy import SQLAlchemy
from model import Location, Department, Category, Subcategory, Base, Sku

engine = create_engine('sqlite:///location_details.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


@app.route('/')
def main():
    """
    This is the main method gets called on running the app and returns
    the location details search page
    """
    return render_template('index.html')

def fetch_all_details():
    """
    """
    query_obj = (session.query(Sku.sku_id,
                              Sku.name,
                              Location.location_desc,
                              Department.department_name,
                              Category.category_desc,
                              Subcategory.sub_category_desc,
                              Location.location_id,
                              Category.category_id,
                              Subcategory.sub_category_id,
                              Department.department_id)
                        .join(Location, Location.location_id == Sku.location_id)
                        .join(Department, Department.department_id == Sku.department_id)
                        .join(Category, Category.category_id == Sku.category_id)
                        .join(Subcategory, Subcategory.sub_category_id == Sku.sub_category_id))
    return query_obj

@app.route('/searchDetails', methods=['GET', 'POST'])
def searchDetails():
    """
    This menthod returns the data based on search input parameters
    If there are no input parameters provided then it returns all the data present in DB
    """
    if request.method == 'POST':
        location = request.form['location']
        department = request.form['department']
        category = request.form['category']
        subcategory = request.form['subcategory']
    else:
        location, department, category, subcategory = '', '', '', ''
    query_obj = fetch_all_details()
    query_obj = query_obj.filter(Sku.name.isnot(None))
    if location:
        query_obj = query_obj.filter(Location.location_desc == location)
    if department:
        query_obj = query_obj.filter(Department.department_name == department)
    if category:
        query_obj = query_obj.filter(Category.category_desc == category)
    if subcategory:
        query_obj = query_obj.filter(Subcategory.sub_category_desc == subcategory)
    data = query_obj.all()
    return render_template('index.html', data=data)

@app.route('/saveDetails',methods=['POST','GET'])
def saveLocationDetails():
    """
    This function is to save all the details into
    DB what user has provided from UI
    """
    try:
        location = request.form['location']
        department = request.form['department']
        category = request.form['category']
        subcategory = request.form['subcategory']
        # validate the received values
        if location and department and category and subcategory:
            loc_obj = Location(location_desc=location)
            dep_obj = Department(department_name=department)
            cat_obj = Category(category_desc=category)
            sub_cat_obj = Subcategory(sub_category_desc=subcategory)
            session.add(loc_obj)
            session.add(dep_obj)
            session.add(cat_obj)
            session.add(sub_cat_obj)
            session.commit()
            sku_obj = Sku(location_id=loc_obj.location_id, department_id=dep_obj.department_id,
                          category_id=cat_obj.category_id, sub_category_id=sub_cat_obj.sub_category_id)
            session.add(sku_obj)
            session.commit()
            session.query(Sku).filter(Sku.sku_id == sku_obj.sku_id).update({'name': 'SKUDESC' + str(sku_obj.sku_id)})
            session.commit()
            return redirect('/')
        else:
            return json.dumps({'error':'<span>Please enter the required fields</span>'})

    except Exception as e:
        app.logger.error(str(e))

@app.route('/addDetails', methods=['GET'])
def addDetails():
    """
    Function to redirect an user to add details page from the landing
    search screen
    """
    return render_template('/add-details-page.html')

@app.route('/deleteRecords/<int:sk_id>', methods=['GET', 'POST'])
def deleteRecords(sk_id):
    """
    Function to delete the specific record from DB based on SK_ID
    Based on SK_ID, we will fetch the corresponding location, deparment, category
    and sub category idns and deletes them from the respective tables
    """
    sku_data = session.query(Sku.location_id,
                                 Sku.department_id,
                                 Sku.category_id,
                                 Sku.sub_category_id).filter(Sku.sku_id == sk_id).all()
    sku_obj = session.query(Sku).filter(Sku.sku_id == sk_id)
    sku_obj.delete(synchronize_session=False)
    loc_obj = session.query(Location).filter(Location.location_id == sku_data[0][0])
    loc_obj.delete(synchronize_session=False)
    dep_obj = session.query(Department).filter(Department.department_id == sku_data[0][1])
    dep_obj.delete(synchronize_session=False)
    cat_obj = session.query(Category).filter(Category.category_id == sku_data[0][2])
    cat_obj.delete(synchronize_session=False)
    sub_cat_obj = session.query(Subcategory).filter(Subcategory.sub_category_id == sku_data[0][3])
    sub_cat_obj.delete(synchronize_session=False)
    session.commit()
    return redirect('/searchDetails')

@app.route('/fetchUpdateRecords/<int:sk_id>', methods=['GET'])
def fetchUpdateRecords(sk_id):
    """
    Function to show the existing added data to an user before he is gonna
    modify it.
    """
    query_obj = fetch_all_details()
    data = query_obj.filter(Sku.sku_id == sk_id).all()
    return render_template('/add-details-page.html', data=data)

@app.route('/updateDetails', methods=['GET', 'POST'])
def updateDetails():
    """
    Function to update all the records based on input
    parameters user has updated
    """
    location = request.form['location']
    department = request.form['department']
    category = request.form['category']
    subcategory = request.form['subcategory']
    location_id = int(request.form['location_id'])
    department_id = int(request.form['department_id'])
    category_id = int(request.form['category_id'])
    sub_cat_id = int(request.form['sub_cat_id'])
    session.query(Location).filter(Location.location_id == location_id).update({'location_desc': location})
    session.query(Department).filter(Department.department_id == department_id).update({'department_name': department})
    session.query(Category).filter(Category.category_id == category_id).update({'category_desc': category})
    session.query(Subcategory).filter(Subcategory.sub_category_id == sub_cat_id).update({'sub_category_desc': subcategory})
    session.commit()
    return redirect('/searchDetails')

# API calling functions start here

@app.route('/api/v1/location', methods=['GET'])
def getAllLocations():
    """
    This is a GET request API to fetch all the locations
    present in DB
    """
    query_obj = session.query(Location)
    payload = []
    for each in query_obj.all():
        payload.append({'location_id': each.location_id, 'location_desc': each.location_desc})
    return json.dumps(payload)

@app.route('/api/v1/location/<int:loc_id>/department', methods=['GET'])
def getAllDepartmentDetails(loc_id=0):
    """
    This is a GET api to fetch the department data based
    on location id
    """
    payload = []
    query_obj = (session.query(Department.department_id,
                              Department.department_name,
                              Location.location_id,
                              Location.location_desc)
                            .join(Sku, Sku.department_id == Department.department_id)
                            .join(Location, Location.location_id == Sku.location_id)
                            .filter(Sku.location_id == loc_id))
    for each in query_obj.all():
        payload.append({'location_id': each[2], 'location_desc': each[3], \
                       'department_id': each[0], 'department_name': each[1]})
    return json.dumps(payload)

@app.route('/api/v1/location/<int:loc_id>/department/<int:depart_id>/category', methods=['GET'])
def getAllCategoryDetails(loc_id=0, depart_id=0):
    """
    GET API to fetch the data based location id
    and department id
    """
    payload = []
    query_obj = (session.query(Department.department_id,
                              Department.department_name,
                              Location.location_id,
                              Location.location_desc,
                              Category.category_id,
                              Category.category_desc)
                        .join(Sku, Sku.department_id == Department.department_id)
                        .join(Location, Location.location_id == Sku.location_id)
                        .join(Category, Category.category_id == Sku.category_id)
                        .filter(and_(Sku.location_id == loc_id, Department.department_id == depart_id)))
    for each in query_obj.all():
        payload.append({'location_id': each[2], 'location_desc': each[3], \
                       'department_id': each[0], 'department_name': each[1], \
                       'category_id': each[4], 'category_desc': each[5]})
    return json.dumps(payload)

def _get_all_sub_categories():
    """
    """
    query_obj = (session.query(Department.department_id,
                              Department.department_name,
                              Location.location_id,
                              Location.location_desc,
                              Category.category_id,
                              Category.category_desc,
                              Subcategory.sub_category_id,
                              Subcategory.sub_category_desc)
                        .join(Sku, Sku.department_id == Department.department_id)
                        .join(Location, Location.location_id == Sku.location_id)
                        .join(Category, Category.category_id == Sku.category_id)
                        .join(Subcategory, Subcategory.sub_category_id == Sku.sub_category_id))
    return query_obj

@app.route('/api/v1/location/<int:loc_id>/department/<int:depart_id>/category/<int:catg_id>/subcategory', methods=['GET'])
def getAllSubCategoryDetails(loc_id=0, depart_id=0, catg_id=0):
    """
    Get API to fetch the data based on location id,
    department id and category id
    """
    payload = []
    query_obj = _get_all_sub_categories()
    query_obj = query_obj.filter(and_(Sku.location_id == loc_id,
                                     Department.department_id == depart_id,
                                     Category.category_id == catg_id))
    for each in query_obj.all():
        payload.append({'location_id': each[2], 'location_desc': each[3], \
                       'department_id': each[0], 'department_name': each[1], \
                       'category_id': each[4], 'category_desc': each[5],
                       'sub_category_id': each[6], 'sub_category_desc': each[7]})
    return json.dumps(payload)

@app.route('/api/v1/location/<int:loc_id>/department/<int:depart_id>/category/<int:catg_id>/subcategory/<int:sub_cat_id>',
            methods=['GET'])
def getAllSubCategoryDetailsWithCategoryId(loc_id=0, depart_id=0, catg_id=0, sub_cat_id=0):
    """
    GET api to fetch all the data based on input
    parameters
    """
    payload = []
    query_obj = _get_all_sub_categories()
    query_obj = query_obj.filter(and_(Sku.location_id == loc_id,
                                     Department.department_id == depart_id,
                                     Category.category_id == catg_id,
                                     Subcategory.sub_category_id == sub_cat_id))
    for each in query_obj.all():
        payload.append({'location_id': each[2], 'location_desc': each[3], \
                       'department_id': each[0], 'department_name': each[1], \
                       'category_id': each[4], 'category_desc': each[5],
                       'sub_cat_id': each[6], 'sub_cat_desc': each[7]})
    return json.dumps(payload)

# DELETE API starts here
@app.route('/api/v2/location/<int:loc_id>', methods=['DELETE'])
def deleteLocationAt(loc_id=0):
    """
    Deletes the data from DB based on the given location id
    """
    sku_obj = session.query(Sku).filter(Sku.location_id == loc_id)
    loc_obj = session.query(Location).filter(Location.location_id == loc_id)
    sku_obj.delete(synchronize_session=False)
    loc_obj.delete(synchronize_session=False)
    session.commit()
    return json.dumps({"Msg": "Record has been deleted successfully"})

# POST API starts here
@app.route('/api/v3/location', methods=['POST'])
def insertLocation():
    """
    Inserts the data into location table which is passed in payload
    """
    if not request.json:
        abort(400)
    location_desc = str(request.json.get('location_desc'))
    loc_obj = Location(location_desc=location_desc)
    session.add(loc_obj)
    session.commit()
    query_obj = session.query(Location).filter(Location.location_id == loc_obj.location_id)
    sample_data = {}
    for each in query_obj.all():
        sample_data['location_id'] = each[0]
        sample_data['location_desc'] = each[1]
    app.logger.info("Data has been inserted successfully")
    return jsonify(sample_data)

# PUT API starts here

@app.route('/api/v4/location', methods=['PUT'])
def updateLocation():
    """
    Updates the location description based on location id
    """
    if not request.json:
        abort(400)
    location_desc = str(request.json.get('location_desc'))
    location_id = int(request.json.get('location_id'))
    session.query(Location).filter(Location.location_id == location_id).update({'location_desc': location_desc})
    session.commit()
    query_obj = session.query(Location).filter(Location.location_id == location_id)
    sample_data = {}
    for each in query_obj.all():
        sample_data['location_id'] = each[0]
        sample_data['location_desc'] = each[1]
    app.logger.info("Data has been updated successfully")
    return jsonify(sample_data)

if __name__ == "__main__":
    app.run()




# curl GET "http://127.0.0.1:5000/api/v1/location/12/department/11/category/11/subcategory/11"