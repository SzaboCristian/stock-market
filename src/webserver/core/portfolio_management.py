import time

from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from webserver.constants import TIME_RANGES
from webserver.decorators import fails_safe_request
from webserver.model.portfolio import (
    Allocation,
    AllocationException,
    Portfolio,
    PortfolioException,
)
from webserver.model.user import User


class PortfolioManagementAPI:
    @staticmethod
    def check_user_exists(user_id) -> bool:
        """
        Check if user with user_id exists in SQL db.
        @param user_id: string
        @return: boolean
        """
        user = User.query.filter_by(public_id=user_id).first()
        if not user:
            return False
        return True

    @staticmethod
    @fails_safe_request
    def get_portfolio(user_id, portfolio_id=None, **kwargs) -> tuple:
        """
        Get portfolio with portfolio_id for specified user. If portfolio id not specified, return all current user
        portfolios. No need for portfolio validation as they were alreay validated on creation/update.
        @param user_id: string
        @param portfolio_id: string
        @param kwargs: dict
        @return: tuple
        """

        if "test" not in kwargs and not PortfolioManagementAPI.check_user_exists(
            user_id
        ):
            return 404, {}, "User not found."

        es_query = {"query": {"bool": {"must": [{"match": {"user_id": user_id}}]}}}
        if portfolio_id:
            es_query["query"]["bool"]["must"].append({"term": {"_id": portfolio_id}})

        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )
        es_portfolio_documents = es_dbi.search_documents(
            config.ES_INDEX_PORTFOLIOS, query_body=es_query
        )
        if es_portfolio_documents and es_portfolio_documents.get("hits", {}).get(
            "hits", []
        ):
            return (
                200,
                {
                    portfolio["_id"]: portfolio["_source"]
                    for portfolio in es_portfolio_documents["hits"]["hits"]
                },
                "OK",
            )

        return 404, {}, "Portfolio not found."

    @staticmethod
    @fails_safe_request
    def create_portfolio(user_id, allocations, **kwargs) -> tuple:
        """
        Create portfolio for user.
        @param user_id: string
        @param allocations: list of dicts [{'ticker': <>, 'percentage': <>}]
        @param kwargs: dict
        @return: tuple
        """

        if "test" not in kwargs and not PortfolioManagementAPI.check_user_exists(
            user_id
        ):
            return 404, {}, "User not found."

        # porotofolio validation
        allocation_objects = []
        for allocation in allocations:
            try:
                allocation_objects.append(Allocation(allocation_json=allocation))
            except AllocationException:
                return 400, "Invalid allocation {}".format(allocation)

        try:
            portfolio = Portfolio(
                portfolio_json={
                    "portfolio_name": kwargs.get(
                        "portfolio_name", "user_portfolio_default"
                    ),
                    "created_timestamp": int(time.time()),
                    "modified_timestamp": int(time.time()),
                    "user_id": user_id,
                    "allocations": allocation_objects,
                }
            )
        except PortfolioException as e:
            return 400, {}, str(e)

        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )
        portfolio_id = es_dbi.create_document(
            config.ES_INDEX_PORTFOLIOS, document=portfolio.get_data()
        )

        if portfolio_id:
            return 200, {"portfolio_id": portfolio_id}, "OK"

        return 500, {}, "Could not create portfolio."

    @staticmethod
    @fails_safe_request
    def update_portfolio(user_id, portfolio_id, new_allocations, **kwargs) -> tuple:
        """
        Update user portfolio.
        @param user_id: string
        @param portfolio_id: string
        @param new_allocations: list of dicts [{'ticker': <>, 'percentage': <>}]
        @param kwargs: dict
        @return: tuple
        """

        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )
        portfolio_document = es_dbi.get_document_by_id(
            config.ES_INDEX_PORTFOLIOS, _id=portfolio_id
        )
        if not portfolio_document:
            return 404, {}, "Portfolio not found."

        if portfolio_document["_source"]["user_id"] != user_id:
            return 401, {}, "Cannot update other users' portfolios"

        # updated data validation
        new_allocation_objects = []
        for new_allocation in new_allocations:
            try:
                new_allocation_objects.append(
                    Allocation(allocation_json=new_allocation)
                )
            except AllocationException:
                return 400, "Invalid allocation {}".format(new_allocation)

        # update portfolio + validation
        try:
            portfolio = Portfolio(
                portfolio_json={
                    "portfolio_name": portfolio_document["_source"].get(
                        "portfolio_name", None
                    ),
                    "created_timestamp": portfolio_document["_source"].get(
                        "created_timestamp", None
                    ),
                    "modified_timestamp": portfolio_document["_source"].get(
                        "modified_timestamp", None
                    ),
                    "user_id": portfolio_document["_source"].get("user_id", None),
                    "allocations": new_allocation_objects,
                }
            )
        except PortfolioException as e:
            return 400, {}, str(e)

        portfolio.set_modified_timestamp(int(time.time()))
        if kwargs.get("portfolio_name", None):
            portfolio.set_portfolio_name(kwargs["portfolio_name"])

        if es_dbi.update_document(
            config.ES_INDEX_PORTFOLIOS, _id=portfolio_id, document=portfolio.get_data()
        ):
            return 200, {"portfolio_id": portfolio_id}, "OK"

        return 500, {}, "Could not update portfolio."

    @staticmethod
    @fails_safe_request
    def backtest_portfolio(
        user_id,
        portfolio_id,
        start_ts=TIME_RANGES["LAST_5_YEARS"],
        ends_ts=int(time.time()),
    ) -> tuple:
        """
        Backtest user portfolio. Default interval 5 years ago - now.
        @param user_id: string
        @param portfolio_id: string
        @param start_ts: int
        @param ends_ts: int
        @return: tuple
        """

        # check portfolio exists
        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )
        portfolio_document = es_dbi.get_document_by_id(
            config.ES_INDEX_PORTFOLIOS, _id=portfolio_id
        )
        if not portfolio_document:
            return 404, {}, "Portfolio not found."

        # check portfolio owner
        if portfolio_document["_source"]["user_id"] != user_id:
            return 401, {}, "Cannot backtest other users' portfolios"

        # setup alloation objects
        allocation_objects = []
        for allocation in portfolio_document["_source"]["allocations"]:
            try:
                allocation_objects.append(Allocation(allocation_json=allocation))
            except AllocationException:
                return 400, "Invalid allocation {}".format(allocation)

        # setup portfolio object
        try:
            portfolio = Portfolio(
                portfolio_json={
                    "portfolio_name": portfolio_document["_source"].get(
                        "portfolio_name", None
                    ),
                    "created_timestamp": portfolio_document["_source"].get(
                        "created_timestamp", None
                    ),
                    "modified_timestamp": portfolio_document["_source"].get(
                        "modified_timestamp", None
                    ),
                    "user_id": portfolio_document["_source"].get("user_id", None),
                    "allocations": allocation_objects,
                }
            )
        except PortfolioException as e:
            return 400, {}, str(e)

        return 200, portfolio.backtest(start_ts=start_ts, end_ts=ends_ts), "OK"

    @staticmethod
    @fails_safe_request
    def delete_portfolio(user_id, portfolio_id) -> tuple:
        """
        Delete user portfolio.
        @param user_id: string
        @param portfolio_id: string
        @return: tuple
        """

        # check portfolio exists
        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )
        portfolio_document = es_dbi.get_document_by_id(
            config.ES_INDEX_PORTFOLIOS, _id=portfolio_id
        )
        if not portfolio_document:
            return 404, {}, "Portfolio not found."

        if portfolio_document["_source"]["user_id"] != user_id:
            return 401, {}, "Cannot delete other users' portfolios"

        # delete
        if es_dbi.delete_document(config.ES_INDEX_PORTFOLIOS, _id=portfolio_id):
            return 200, {}, "OK"

        return 500, {}, "Could not delete portfolio."
