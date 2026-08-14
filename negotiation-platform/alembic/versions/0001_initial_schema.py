"""Initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-07-19 04:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    op.create_table('negotiations',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', UUID(as_uuid=True), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('state_payload', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('businesses',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('negotiation_id', UUID(as_uuid=True), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['negotiation_id'], ['negotiations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('quotes',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('negotiation_id', UUID(as_uuid=True), nullable=True),
    sa.Column('business_id', UUID(as_uuid=True), nullable=True),
    sa.Column('amount', sa.String(), nullable=True),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.ForeignKeyConstraint(['negotiation_id'], ['negotiations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('calls',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('negotiation_id', UUID(as_uuid=True), nullable=True),
    sa.Column('business_id', UUID(as_uuid=True), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('outcome', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.ForeignKeyConstraint(['negotiation_id'], ['negotiations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('transcripts',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('call_id', UUID(as_uuid=True), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['call_id'], ['calls.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('reports',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('negotiation_id', UUID(as_uuid=True), nullable=True),
    sa.Column('report_url', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['negotiation_id'], ['negotiations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('transcripts')
    op.drop_table('calls')
    op.drop_table('quotes')
    op.drop_table('businesses')
    op.drop_table('negotiations')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
