from src.models import db, BusinessItems

class BusinessItem:
    
    def get_all_items(self):
        '''Returns rating by post id'''
        items = BusinessItems.query.all()
        return items
    
    def get_business_items_by_user_id(self, user_id):
        '''Returns all ratings'''
        return BusinessItems.query.filter_by(business_id=user_id).scalar()
    
    def get_menu_title(self, user_id):
        '''Returns all menu titles'''
        business_items = self.get_business_items_by_user_id(user_id)
        return business_items.menu_title
    
    def create_business_items(self, user_id):
        '''Creates business items'''
        business_items = BusinessItems(business_id=user_id)
        db.session.add(business_items)
        db.session.commit()
        return business_items

    def get_menu(self, user_id):
        '''Returns all menus'''
        business_items = self.get_business_items_by_user_id(user_id)
        return business_items.menu_file
    
    def ammend_features(self, user_id, features):
        '''Change or add features'''
        business_items = self.get_business_items_by_user_id(user_id)
        business_items.features=features
        db.session.commit()
        return  business_items.features
    
    # def add_menu():
    #     '''Add menu'''
    #     pass

business_items = BusinessItem()