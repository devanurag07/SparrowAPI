from .views import ConversationAPI,ChatAPI,StatusAPI
from rest_framework.routers import SimpleRouter



router=SimpleRouter()
router.register("chats",ChatAPI,basename="chat_api")
router.register("conv",ConversationAPI,basename="conv_api")
router.register("status",StatusAPI,basename="status_api")

urlpatterns = router.urls
