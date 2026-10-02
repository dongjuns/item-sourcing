"""수집한 표준 모델로 수량별 상품금액을 계산한다. 주문은 실행하지 않는다."""

from decimal import Decimal

from app.schemas.product import Issue, ProductData, ProductQuote


def product_quote(
    product: ProductData, quantity: int, option_id: str | None = None
) -> ProductQuote:
    result = ProductQuote(quantity=quantity, currency=product.currency)
    if quantity < (product.minimum_order_quantity or 1):
        result.issues.append(Issue(code="minimum_quantity", message="최소 주문 수량보다 적습니다."))
    if product.purchase_unit and quantity % product.purchase_unit:
        result.issues.append(Issue(code="purchase_unit", message="구매 단위의 배수로 입력하세요."))
    maximum = product.maximum_order_quantity
    if maximum is not None and quantity > maximum:
        result.issues.append(Issue(code="maximum_quantity", message="최대 주문 수량을 넘었습니다."))
    if product.stock_quantity is not None and quantity > product.stock_quantity:
        result.issues.append(Issue(code="stock_quantity", message="수집 시점 재고보다 많습니다."))
    if result.issues:
        return result
    result.unit_price = product.wholesale_price
    for tier in product.price_tiers:
        if quantity >= tier.minimum_quantity:
            result.unit_price = tier.unit_price
    if product.options:
        option = next((row for row in product.options if row.source_option_id == option_id), None)
        if option is None or option.wholesale_price is None:
            result.issues.append(
                Issue(code="option_price", message="옵션과 실제 옵션 단가 확인 필요")
            )
            return result
        result.unit_price = option.wholesale_price
        if option.available is False or (
            option.stock_quantity is not None and quantity > option.stock_quantity
        ):
            result.issues.append(Issue(code="option_stock", message="선택 옵션 재고를 확인하세요."))
            return result
    if result.unit_price is not None:
        result.product_amount = result.unit_price * quantity
    else:
        result.issues.append(Issue(code="missing_price", message="수량에 적용할 단가 확인 필요"))
    return add_shipping(product, result)


def add_shipping(product: ProductData, result: ProductQuote) -> ProductQuote:
    shipping = product.shipping
    if shipping is not None:
        if shipping.payment_method == "무료배송":
            result.shipping_fee = Decimal(0)
        elif shipping.fee_calculation == "fixed":
            result.shipping_fee = shipping.fee
        elif shipping.fee_calculation == "quantity_tiers":
            for tier in shipping.quantity_fee_tiers:
                if result.quantity >= tier.minimum_quantity:
                    result.shipping_fee = tier.unit_price
    if result.shipping_fee is None:
        result.issues.append(Issue(code="shipping_unknown", message="수량별 배송비 확인 필요"))
    if result.product_amount is not None and result.shipping_fee is not None:
        result.total_amount = result.product_amount + result.shipping_fee
    result.issues.append(
        Issue(
            code="quote_scope",
            message="일반 지역 기본 배송비 기준. 추가 배송비·할인·다른 상품 묶음배송 제외",
        )
    )
    return result
