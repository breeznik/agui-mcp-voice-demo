import { FlightCard, WeatherCard, HotelCard, ItineraryCard } from './cards/TravelCards'
import { QuestionCard, AnswerCard, ScoreboardCard, CategoryCard } from './cards/TriviaCards'
import { ProductCard, CartCard, CheckoutCard } from './cards/ShoppingCards'
import { OrderCard, TicketCard, KbArticleCard, EscalationCard } from './cards/SupportCards'
import { RecipeCard, NutritionCard, MealPlanCard, ShoppingListCard } from './cards/ChefCards'

// Component registry — maps card_type → React component
export const CARD_REGISTRY = {
    // Travel
    flight_card: FlightCard,
    weather_card: WeatherCard,
    hotel_card: HotelCard,
    itinerary_card: ItineraryCard,

    // Trivia
    question_card: QuestionCard,
    answer_card: AnswerCard,
    scoreboard_card: ScoreboardCard,
    category_card: CategoryCard,

    // Shopping
    product_card: ProductCard,
    cart_card: CartCard,
    checkout_card: CheckoutCard,

    // Chef
    recipe_card: RecipeCard,
    nutrition_card: NutritionCard,
    meal_plan_card: MealPlanCard,
    shopping_list_card: ShoppingListCard,

    // Support
    order_card: OrderCard,
    ticket_card: TicketCard,
    kb_article_card: KbArticleCard,
    escalation_card: EscalationCard,
};
