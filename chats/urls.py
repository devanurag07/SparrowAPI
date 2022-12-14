from .views import ConversationAPI,ChatAPI
from rest_framework.routers import SimpleRouter



router=SimpleRouter()
router.register("chats",ChatAPI,basename="chat_api")
router.register("conv",ConversationAPI,basename="conv_api")

urlpatterns = router.urls
