from flask import Blueprint, request, jsonify
from production_cost.models import GrossProfit
from production_cost import logger


costs = Blueprint("costs", __name__, url_prefix="/api/margin")


@costs.route("/amp-production-cost", methods=["GET"])
def get_amp_production_cost():
    try:
        data = request.args
        logger.info(f"PARAMS :  {data}")
        print(f"PARAMS :  {data}")
        result = GrossProfit.get(**data)
    except Exception as e:
        logger.exception(e)
        print(e)
        return jsonify({"Success": False, "Errors": str(e)}), 400
    print(f"Send data : {result}")
    logger.info(f"Send data : {result}")
    return jsonify(result), 200
