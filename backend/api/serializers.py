from users.models import User, Hardskill, Achievement, Contact
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from tasks.models import Task, TaskUpdate, TaskInvitation


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('contact_type', 'link')


class AchievementSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Achievement
        fields = ('name', 'image', 'description')


class HardskillsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hardskill
        fields = ('name',)


class CustomUserRetrieveSerializer(UserSerializer):
    hardskills = HardskillsSerializer(many=True, required=False)
    achievements = AchievementSerializer(many=True, required=False)
    hardskills_read_only = serializers.BooleanField(read_only=True, default=False)
    achievements_read_only = serializers.BooleanField(read_only=True, default=False)
    reward_points = serializers.IntegerField(read_only=True)
    contacts = ContactSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'birthday',
                  'email',
                  'hardskills',
                  'achievements',
                  'role',
                  'position',
                  'hardskills_read_only',
                  'achievements_read_only',
                  'reward_points',
                  'contacts')

    def update(self, instance, validated_data):
        hardskills_data = validated_data.pop('hardskills', [])
        achievements_data = validated_data.pop('achievements', [])
        contacts_data = validated_data.pop('contacts', [])

        is_teamleader = self.context['request'].user.is_teamleader
        is_user_self = instance == self.context['request'].user

        if is_teamleader:
            instance.hardskills.clear()
            instance.achievements.clear()

            for hardskill_data in hardskills_data:
                hardskill, created = Hardskill.objects.get_or_create(
                    name=hardskill_data['name'])
                instance.hardskills.add(hardskill)

            for achievement_data in achievements_data:
                achievement, created = Achievement.objects.get_or_create(
                    name=achievement_data['name'],
                    defaults={'description': achievement_data.get('description', '')}
                )
                instance.achievements.add(achievement)

        if is_user_self:
            for contact_data in contacts_data:
                contact_type = contact_data.get('contact_type')
                link = contact_data.get('link')
                if contact_type and link:

                    contact, created = Contact.objects.update_or_create(
                        user=instance,
                        contact_type=contact_type,
                        defaults={'link': link}
                    )
        instance = super().update(instance, validated_data)
        return instance


class CustomUserCreateSerializer(UserCreateSerializer):
    password_confirmation = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'})

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + (
            'password_confirmation',
        )

    def validate(self, data):
        if data["password"] != data.get("password_confirmation"):
            raise serializers.ValidationError("Пароли должны совпадать.")

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")

        required_fields = [
            "email", "password", "password_confirmation",
            "first_name", "last_name"
        ]
        if any(field not in data for field in required_fields):
            raise serializers.ValidationError("Не все обязательные поля заполнены.")
        data.pop("password_confirmation")
        return data


class TaskSerializer(serializers.ModelSerializer):
    team_leader = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.CharField(default='created')

    class Meta:
        model = Task
        fields = '__all__'


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskUpdate
        fields = '__all__'


class TaskInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskInvitation
        fields = '__all__'


class ShortUserProfileSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'image',
            'reward_points',
            'rating',
            'department'
        )

    def get_rating(self, obj):
        users = User.objects.filter(is_active=True).order_by('-reward_points', 'email')
        user_ids = [user.id for user in users]
        rating = user_ids.index(obj.id) + 1
        return rating