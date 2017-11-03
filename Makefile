
default:
	@echo "This will install ansible-check-insights onto this system"
	@echo
	@echo "   sudo make install"

install:
	install -D --target-directory=/usr/bin bin/ansible-check-insights
	install -D --target-directory=/usr/share/ansible-check-insights/plugins/action_plugins share/ansible-check-insights/plugins/action_plugins/check.py
	install -D --target-directory=/usr/share/ansible-check-insights/plugins/callback_plugins share/ansible-check-insights/plugins/callback_plugins/notify_insights.py
	install -D --target-directory=/usr/share/ansible-check-insights/plugins/library share/ansible-check-insights/plugins/library/check.py
