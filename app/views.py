from flask import Blueprint,jsonify,request
from .models import User, Campaign, Contribution, Category
from datetime import datetime
from .import db
from flask_jwt_extended import jwt_required,get_jwt_identity

views=Blueprint('views',__name__)

@views.route('/')
@jwt_required()
def home():
    return {"message":"hi"}

@views.route('/profile')
@jwt_required()
def get_profile():
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    if user:
        return {"username":user.username, "id":user.id, "email":user.email,'profile_img_url':user.profile_img_url, "created_at":user.created_at},200
    return {"err":"user not found"},404

@views.route('/create-campaign',methods=['POST'])
@jwt_required()
def create_campaign():
    user_id=get_jwt_identity()
    # user=User.query.get(user_id)

    title = request.json.get('title')
    desc = request.json.get('desc')
    goal_amount = request.json.get('target')
    start_date_str = request.json.get('start_date')
    deadline_str = request.json.get('deadline')
    thumbnail_img = request.json.get('thumbnail_img')
    campaign_images = request.json.get('campaign_images')  # Expecting list of URLs
    category_id = request.json.get('category_id')

    if not all([title, desc, goal_amount, deadline_str, thumbnail_img, category_id,start_date_str]):
        return {"err": "Missing required parameters"}, 400

    try:
        goal_amount = float(goal_amount.replace(",", ""))
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        return {"error": "Invalid date format. Use 'YYYY-MM-DD' format."}, 400
    
    if not isinstance(campaign_images, list):
        return {"err": "campaign_images should be a list of URLs"}, 400

    new_campaign = Campaign(
        title=title,
        description=desc,
        goal_amount=goal_amount,
        deadline=deadline,
        start_date=start_date,
        creator_id=user_id,
        img_url=thumbnail_img,  # img_url is the thumbnail image
        campaign_images=campaign_images,
        category_id=category_id
    )
    try:
        db.session.add(new_campaign)
        db.session.commit()
        return {"message":"created new campaign"},201
    except Exception as e:
        return {"error":f"Failed to create campaign {e}"},500
    
@views.route('/get-campaigns')
# @jwt_required()
def get_campaigns():
    user_id=request.args.get('user_id')
    if(user_id):
        campaigns=Campaign.query.filter_by(creator_id=user_id).all()
    else:
        campaigns=Campaign.query.all()
    if campaigns:
        return {
            "count":len(campaigns),
            "campaigns":[
                {
                "id":campaign.id,
                "title":campaign.title,
                "description":campaign.description,
                "goal_amount":campaign.goal_amount,
                "collected_amount":campaign.collected_amount,
                "deadline": campaign.deadline.strftime('%Y-%m-%d'),
                "start_date": campaign.start_date,
                "img_url":campaign.img_url,
                "creator_id":campaign.creator_id,
                "creator_name":campaign.creator.username if campaign.creator else None,
                "creator_img":campaign.creator.profile_img_url if campaign.creator else None,
                "campaign_images":campaign.campaign_images,
                "category_id":campaign.category_id,
                "category_name":campaign.category.name if campaign.category else None,
                } for campaign in campaigns
            ]
        }
    
@views.route('/get-my-campaigns')
@jwt_required()
def get_my_campaigns():
    user_id=get_jwt_identity()
    campaigns=Campaign.query.filter_by(creator_id=user_id).all()

    if not campaigns:
        return {"message":"No campaigns found"},404
    return {
            "count":len(campaigns),
            "campaigns":[
                {
                "id":campaign.id,
                "title":campaign.title,
                "description":campaign.description,
                "category_id":campaign.category_id,
                "goal_amount":campaign.goal_amount,
                "collected_amount":campaign.collected_amount,
                "deadline": campaign.deadline.strftime('%Y-%m-%d'),
                "start_date": campaign.start_date,
                "img_url":campaign.img_url,
                "creator_id":campaign.creator_id,
                "creator_name":campaign.creator.username if campaign.creator else None,
                "campaign_images":campaign.campaign_images,
                } for campaign in campaigns
            ]
        }

@views.route('/delete-campaign/<int:id>')
@jwt_required()
def delete_campaign(id):
    user_id = get_jwt_identity()
    campaign = Campaign.query.get(id)
    
    if campaign:
        if campaign.creator_id == int(user_id):
            # First delete all associated contributions
            Contribution.query.filter_by(campaign_id=id).delete()
            # Then delete the campaign
            db.session.delete(campaign)
            db.session.commit()
            return {"message": "campaign deleted"}, 200
        else:
            return {"error": "unauthorized access"}, 400
    else:
        return {"err": "campaign not found"}, 404
    
@views.route('/update-campaign/<int:id>',methods=['PUT'])
@jwt_required()
def update_campaign(id):
    user_id=get_jwt_identity()
    campaign=Campaign.query.get(id)
    campaign_images=request.json.get('campaign_images')
    if campaign and campaign_images:
        campaign.campaign_images=campaign_images
        db.session.commit()
        return {"message":"campaign updated"},200
    return {"err":"campaign not found"},404
    
@views.route('/updated-collected-amt/<int:campagin_id>', methods=["PUT"])
@jwt_required()
def update_collected_amt(campagin_id):
    campaign=Campaign.query.get(campagin_id)
    if campaign:
        amt=request.json.get('amt')
        amt = float(amt.replace(",", ""))
        contributor_id=request.json.get('contributor_id')

        if amt is None or contributor_id is None:
            return {"err":"missing required parameters"},400

        campaign.collected_amount+=float(amt)

        new_contribution=Contribution(
            amount=float(amt),
            contributor_id=contributor_id,
            campaign_id=campagin_id
        )
        db.session.add(new_contribution)
        db.session.commit()
        return {"message":f"campaign updated to {campaign.collected_amount}"},200
    else:
        return {"err":"campaign not found"},404
    
@views.route('/get-contributors/<int:campaign_id>')
@jwt_required()
def get_contributors(campaign_id):
    campaign=Campaign.query.get(campaign_id)
    if campaign:
        return {
            "count":len(campaign.contributions),
            "contributors":[
                {
                    "id":contribution.id,
                    "amount":contribution.amount,
                    "contributor_id":contribution.contributor_id,
                    "contributor_name":contribution.contributor.username if contribution.contributor else None,
                    "contributor_img":contribution.contributor.profile_img_url if contribution.contributor else None,
                    "contributed_at":contribution.contributed_at.strftime('%Y-%m-%d'), 
                } for contribution in campaign.contributions
            ]
        }
    return jsonify({"err":"campaign not found"}),404

@views.route('/search-campaigns')
def search_campaigns():
    # Get query parameters
    search_query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('order', 'desc')
    category_id = request.args.get('category_id', None)
    
    # Start with base query
    query = Campaign.query.join(User, Campaign.creator_id == User.id)
    
    # Apply search filter if query exists
    if search_query:
        query = query.filter(
            db.or_(
                Campaign.title.ilike(f'%{search_query}%'),
                Campaign.description.ilike(f'%{search_query}%'),
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%')
            )
        )
    
    # Apply category filter if specified
    if category_id:
        query = query.filter(Campaign.category_id == category_id)
    
    # Apply sorting
    if sort_by in ['title', 'created_at', 'goal_amount', 'collected_amount', 'deadline']:
        sort_column = getattr(Campaign, sort_by)
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    
    # Execute query and get results
    campaigns = query.all()
    
    # Convert to JSON serializable format
    result = []
    for campaign in campaigns:
        result.append({
            'id': campaign.id,
            'title': campaign.title,
            'description': campaign.description,
            'goal_amount': campaign.goal_amount,
            'collected_amount': campaign.collected_amount,
            'deadline': campaign.deadline.strftime('%Y-%m-%d'),
            'start_date': campaign.start_date.isoformat(),
            'creator_id': campaign.creator_id,
            'created_at': campaign.created_at.isoformat(),
            'img_url': campaign.img_url,
            'category_id': campaign.category_id,
            "creator_name":campaign.creator.username if campaign.creator else None,
            "creator_img":campaign.creator.profile_img_url if campaign.creator else None,
        })
    
    return jsonify(result)

@views.route('/get-categories')
def get_categories():
    categories=Category.query.all()
    return {
        "categories":[
            {
                "id":category.id,
                "name":category.name,
                "description":category.description,
            } for category in categories
        ]
    }   
