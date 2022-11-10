from .. import models, schemas, utils
from fastapi import APIRouter,  status, HTTPException, Depends, Request, Response
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, text, case, Date as sqlDate
from typing import List, Optional
from ..oauth2 import restrict_access_to, check_current_user
from datetime import datetime, date
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2.exceptions import TemplateNotFound

router = APIRouter(
    tags=["Views"]
)

template = Jinja2Templates(directory="templates")

# Set up custom filters
template.env.filters["currency"] = utils.currencyFormat
template.env.filters["trantype"] = utils.typeFormat
template.env.filters["totaltran"] = utils.totalAmount


def protected_route(user, req: Request, temp: str = "menu.html", page: str = "", data: dict = {}):
    try:
        context = {"request": req, "user": user,
                   "message": "" if user else "Please Login to access this page",
                   "page": page if user else "login", **data}
        if user is None:
            temp = "home.html"
    except TemplateNotFound:
        context["page"] = "_pagenotfound.html"
    except Exception as err:
        context["message"] = err.args[0]
        context["page"] = "_error.html"
        print(err)
    finally:
        return template.TemplateResponse(
            temp, context
        )


def protected_admin_route(user, req: Request, temp: str = "menu.html", page: str = "", data: dict = {}):
    try:
        context = {"request": req, "user": user,
                   "message": "" if user else "Please Login to access this page",
                   "page": page if user else "login", **data}
        if user:
            if user.clearance != 'admin':
                context["message"] = "Oops You dont have access to this page"
                context["page"] = "_error.html"
        else:
            temp = "home.html"
    except TemplateNotFound:
        context["page"] = "_pagenotfound.html"
    except Exception as err:
        context["message"] = err.args[0]
        context["page"] = "_error.html"
        print(err)
    finally:
        return template.TemplateResponse(
            temp, context
        )


@router.get("/", response_class=HTMLResponse)
async def getHome(req: Request):
    return template.TemplateResponse("home.html", {"request": req})


@router.get("/logout")
async def logout(res: Response, req: Request):
    res.delete_cookie(key="token")
    res.set_cookie(key="token", value=None, expires=2)
    return template.TemplateResponse("home.html", {"request": req, "message": "Logout Successfully"})


@router.get("/register", response_class=HTMLResponse)
async def getRegister(req: Request):
    return template.TemplateResponse("home.html", {"request": req, "page": "register"})


@router.get("/dashboard",  response_class=HTMLResponse)
async def getDashboard(req: Request, user=Depends(check_current_user)):
    return protected_route(
        user, req, page="_profile.html"
    )


@router.get("/dashboard/accounts",  response_class=HTMLResponse)
async def getMyAccounts(req: Request, user=Depends(check_current_user)):
    return protected_route(
        user, req, page="_accounts.html"
    )


@router.get("/dashboard/transactions",  response_class=HTMLResponse)
async def getTransactions(
        req: Request, account_no: str = "", from_d: str = None, to_d: str = None,
        transaction_type: str = "", limit: int = 30, page: int = 1,
        user=Depends(check_current_user),  db: Session = Depends(get_db)):

    transactions = db.query(models.Transaction).where(
        models.Transaction.account_no == account_no, models.Transaction.transaction_type.like(transaction_type))
    if from_d and to_d:
        transactions = transactions.filter(
            models.Transaction.transaction_date.between(from_d, to_d))
    transactions = transactions.order_by(text("transaction_date DESC"))
    transactions = transactions.limit(limit).offset(
        (page - 1) * limit).all()

    return protected_route(
        user, req, page="_transactions.html", data={
            "transactions": transactions, "from_d": from_d, "to_d": to_d,
            "transaction_type": transaction_type, "account_no": account_no
        }
    )


@router.get("/dashboard/banking",  response_class=HTMLResponse)
async def getDashboard(req: Request, user=Depends(check_current_user)):
    return protected_route(
        user, req, page="_banking.html"
    )


# Admin Routes
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def getAdminDashboard(req: Request, user=Depends(check_current_user), db: Session = Depends(get_db)):
    dashboard = {}
    sub_qry = db.query(models.Customer.customer_name, case(
        (models.Customer.created_at < text("NOW() - '2 days'::INTERVAL"), "Old"),
        else_="New"
    ).label('category')).subquery()
    query = db.query(sub_qry.c.category, func.count(
        sub_qry.c.category).label("count")).group_by(sub_qry.c.category)
    dashboard["customers_info"] = query.all()
    dashboard["accounts_info"] = db.query(
        models.Account.account_type, func.count(
            models.Account.account_no).label("no_accounts"),
        func.sum(models.Account.account_balance).label("total_balance")
    ).group_by(models.Account.account_type).all()
    dashboard["transactions_info"] = db.query(
        models.Transaction.transaction_type, func.sum(
            models.Transaction.transaction_amount).label("total")
    ).where(models.Transaction.transaction_date.cast(sqlDate) == date.today()).group_by(models.Transaction.transaction_type).all()
    return protected_admin_route(
        user, req, page="_dashboard.html", data=dashboard
    )


@router.get("/admin/customers", response_class=HTMLResponse)
async def getManageCustomersPage(
    req: Request,
    user=Depends(check_current_user), db: Session = Depends(get_db)
):
    customers = db.query(models.Customer).all()
    return protected_admin_route(
        user, req, page="_customers.html", data={"customers": customers}
    )


@router.get("/admin/transactions", response_class=HTMLResponse)
async def getAllTransactionsPage(req: Request, user=Depends(check_current_user)):
    return protected_admin_route(
        user, req, page="_alltransactions.html"
    )


@router.get("/admin/accounts", response_class=HTMLResponse)
async def getAllAccountsPage(req: Request, user=Depends(check_current_user)):
    return protected_admin_route(
        user, req, page="_allaccounts.html"
    )

# @router.get("/admin/dashboard", response_class=HTMLResponse)
# async def getAdminDashboard(req: Request, user=Depends(check_current_user)):
#     return protected_admin_route(
#         user, req, page="_dashboard.html"
#     )
